#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Standard module
from splthread import SplThread
import defaults
from classes import Movie
from classes import MovieInfo
from messagehandler import Query
import sys
import os
import threading
import ssl
import json
from base64 import b64encode
import argparse
import time
import copy
from io import StringIO
import threading
from datetime import datetime
from pprint import pprint

import time
import urllib
from urllib.request import urlopen, urlretrieve


# Non standard modules (install with pip)


ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))
# own local modules


class SplPlugin(SplThread):
	plugin_id = 'playerhandler'
	plugin_names = ['Users Player']

	def __init__(self, modref):
		''' creates the simulator
		'''
		self.modref = modref

		super().__init__(modref.message_handler, self)
		modref.message_handler.add_event_handler(
			self.plugin_id, 0, self.event_listener)
		modref.message_handler.add_query_handler(
			self.plugin_id, 0, self.query_handler)
		self.runFlag = True

		# plugin specific stuff
		self.players = {}

	def event_listener(self, queue_event):
		''' react on events
		'''
		print("playerhandler event handler",
			  queue_event.type, queue_event.user)
		if queue_event.type == defaults.PLAYER_PLAY_REQUEST:
			device_friedly_name = queue_event.data['device']
			movie = queue_event.data['movie']
			movie_id = queue_event.data['movie_id']
			self.stop_play(device_friedly_name, queue_event.user)
			self.start_play(queue_event.user,
							device_friedly_name, movie, movie_id)
		if queue_event.type == defaults.MSG_SOCKET_PLAYER_KEY:
			self.handle_keys(queue_event)
		if queue_event.type == defaults.MSG_SOCKET_PLAYER_VOLUME:
			self.handle_volume(queue_event)
		if queue_event.type == defaults.MSG_SOCKET_PLAYER_TIME:
			self.handle_time(queue_event)
		if queue_event.type == defaults.DEVICE_PLAY_STATUS:
			self.handle_device_play_status(queue_event)
		return queue_event

	def query_handler(self, queue_event, max_result_count):
		''' answers with list[] of results
		'''
		print("playerhandler query handler", queue_event.type,
			  queue_event.user, max_result_count)
		return[]

	def start_play(self, user, device_friendly_name, movie, movie_id):
		self.players[user] = type('', (object,), {'movie': movie, 'device_friendly_name': device_friendly_name, 'player_info': type('', (object,), {
			'play': True,
			'position': 0,
			'volume': 3,
			'time': 0,
			'playTime': '00:00',
						'remainingTime': '00:00',
						'duration': 90*60
		})()
		})()
		self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_REQUEST, {
			'movie_url': movie.url, 'movie_mime_type': 'video/mp4', 'device_friendly_name': device_friendly_name})
		self.send_app_movie_info(user, movie)
		print('Start play for {0} {1} {2} {3}'.format(
			user, device_friendly_name, movie_id, movie.url))

	def send_app_movie_info(self, user_name, movie):
		app_movie_info = {
			'title': movie.title,
			'category': movie.category,
			'source': movie.source,
			'date': movie.timestamp,
			'duration': movie.duration,
			'viewed': "geschaut",
			'description': movie.description
		}

		self.modref.message_handler.queue_event(user_name, defaults.MSG_SOCKET_MSG, {
			'type': 'app_movie_info', 'config': app_movie_info})

	def pause_play(self, user, device_friendly_name):
		self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_PAUSE, {
			'device_friendly_name': device_friendly_name})
		print('Pause play for {0}'.format(device_friendly_name))

	def resume_play(self, user, device_friendly_name):
		self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_RESUME, {
			'user': user, 'device_friendly_name': device_friendly_name})
		print('Resume play for {0}'.format(device_friendly_name))

	def stop_play(self, user, device_friendly_name):
		self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_STOP, {
			'user': user, 'device_friendly_name': device_friendly_name})
		print('Stop play for {0}'.format(device_friendly_name))

	def handle_volume(self, queue_event):
		user = queue_event.user
		data = queue_event.data
		volume = data['timer_vol']  # volume can be between 0 and 100 (%)
		if self.players[user]:
			user_player = self.players[user]
			self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_SETVOLUME, {
				'device_friendly_name': user_player.device_friendly_name, 'volume': data['timer_vol']})

	def handle_time(self, queue_event):
		user = queue_event.user
		data = queue_event.data
		percent_pos=data['timer_pos']
		if self.players[user]:
			user_player = self.players[user]
			player_info = user_player.player_info
			pos=player_info.duration * percent_pos / 100
			self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_SETPOS, {
				'device_friendly_name': user_player.device_friendly_name, 'pos': pos})


	def handle_keys(self, queue_event):
		user = queue_event.user
		data = queue_event.data
		if self.players[user]:
			new_pos = False
			user_player = self.players[user]
			player_info = user_player.player_info
			if data['keyid'] == 'prev':
				player_info.time = 0
				new_pos = True
			if data['keyid'] == 'minus10':
				player_info.time -= 10*60
				if player_info.time < 0:
					player_info.time = 0
				new_pos = True
			if data['keyid'] == 'play':
				player_info.play = not player_info.play
				if player_info.play:
					self.resume_play(user, user_player.device_friendly_name)
				else:
					self.pause_play(user, user_player.device_friendly_name)
			if data['keyid'] == 'plus10':
				if player_info.time + 10*60 < player_info.duration:
					player_info.time += 10*60
					new_pos = True
			if data['keyid'] == 'next':
				player_info.time = player_info.duration
				player_info.play = False
				new_pos = True
			if new_pos:
				self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_SETPOS, {
					'device_friendly_name': user_player.device_friendly_name, 'pos': player_info.time})

	def handle_device_play_status(self, queue_event):
		data = queue_event.data
		for user_name, user_player in self.players.items(): # does the user has a player?
			player_info = user_player.player_info
			if user_player.device_friendly_name == data['device_friendly_name']:
				player_info.play = data['play']
				player_info.time  = data['time']
				player_info.duration  = data['duration']
				player_info.volume  = data['volume']*100
				if data['state_change']:
					pass
				self.send_player_status(user_name, player_info)


	def send_player_status(self, user_name, player_info):
		if player_info.time and player_info.duration:
			player_info.position = player_info.time * 100 // player_info.duration
			player_info.playTime = '{:02d}:{:02d}'.format(
				int(player_info.time) // 60, int(player_info.time % 60))
			player_info.remainingTime = '{:02d}:{:02d}'.format(
				int (player_info.duration-player_info.time)//60, int(player_info.duration-player_info.time) % 60)
			self.modref.message_handler.queue_event(user_name, defaults.MSG_SOCKET_MSG, {
				'type': 'app_player_pos', 'config': player_info.__dict__})
		print(player_info.__dict__)


	def _run(self):
		''' starts the server
		'''
		while self.runFlag:
			time.sleep(1)

	def _stop(self):
		self.runFlag = False
