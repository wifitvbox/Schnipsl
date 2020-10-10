#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Standard module

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

import urllib
from urllib.request import urlopen, urlretrieve


# Non standard modules (install with pip)


ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))
# own local modules
from splthread import SplThread
import defaults
from classes import Movie
from classes import MovieInfo
from messagehandler import Query

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
		if queue_event.type == '_join':
			# update the App Play info
			user_name = queue_event.user
			self.refresh_app_movie_info(user_name)

		if queue_event.type == defaults.PLAYER_PLAY_REQUEST or queue_event.type == defaults.PLAYER_PLAY_REQUEST_WITHOUT_DEVICE:
			movie = queue_event.data['movie']
			movie_uri = queue_event.data['movie_uri']
			current_time = queue_event.data['current_time']
			device_friendly_name=''
			if queue_event.type == defaults.PLAYER_PLAY_REQUEST_WITHOUT_DEVICE:  # this is a message is send
				feasible_devices = self.modref.message_handler.query(Query(
					queue_event.user, defaults.QUERY_FEASIBLE_DEVICES, movie_uri))
				# is there actual a player playing?
				if not queue_event.user in self.players:  # no player started yet
					self.send_player_devices(
						queue_event.user, feasible_devices, movie_uri)
					return queue_event
				user_player = self.players[queue_event.user]
				if not user_player.player_info.play: # the player is not playing
					self.send_player_devices(
						queue_event.user, feasible_devices, movie_uri)
					return queue_event
				device_friendly_name = user_player.device_friendly_name
				if not device_friendly_name in feasible_devices:  # the actual player cant play it
					self.send_player_devices(
						queue_event.user, feasible_devices, movie_uri)
					return queue_event  # no matching device, so device need to be selected first
			else:
				device_friendly_name = queue_event.data['device']
			self.player_save_state(queue_event.user)
			self.stop_play( queue_event.user, device_friendly_name)
			self.start_play(queue_event.user,
							device_friendly_name, movie, movie_uri, current_time)
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

	def start_play(self, user, device_friendly_name, movie, movie_uri, current_time):
		self.players[user] = type('', (object,), {'movie': movie, 'device_friendly_name': device_friendly_name, 'player_info': type('', (object,), {
			'play': True,
			'position': 0,
			'volume': 3,
			'current_time': current_time,
			'duration': -1
		})()
		})()
		self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_REQUEST, {
			'movie_url': movie.url, 'current_time': current_time, 'movie_mime_type': 'video/mp4', 'device_friendly_name': device_friendly_name})
		self.send_app_movie_info(user, movie)
		print('Start play for {0} {1} {2} {3}'.format(
			user, device_friendly_name, movie_uri, movie.url))

	def send_app_movie_info(self, user_name, movie):
		app_movie_info = {
			'title': movie.title,
			'category': movie.category,
			'provider': movie.provider,
			'timestamp': movie.timestamp,
			'duration': movie.duration,
			'current_time': "geschaut",
			'description': movie.description
		}
		self.modref.message_handler.queue_event(user_name, defaults.MSG_SOCKET_MSG, {
			'type': defaults.MSG_SOCKET_APP_MOVIE_INFO, 'config': app_movie_info})

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
		user_name = queue_event.user
		data = queue_event.data
		volume = data['timer_vol']  # volume can be between 0 and 100 (%)
		if user_name in self.players:
			user_player = self.players[user_name]
			self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_SETVOLUME, {
				'device_friendly_name': user_player.device_friendly_name, 'volume': data['timer_vol']})

	def handle_time(self, queue_event):
		user_name = queue_event.user
		data = queue_event.data
		percent_pos = data['timer_pos']
		if user_name in self.players:
			user_player = self.players[user_name]
			player_info = user_player.player_info
			pos = player_info.duration * percent_pos / 100
			self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_SETPOS, {
				'device_friendly_name': user_player.device_friendly_name, 'pos': pos})

	def handle_keys(self, queue_event):
		user_name = queue_event.user
		data = queue_event.data
		if user_name in self.players:
			new_pos = False
			user_player = self.players[user_name]
			player_info = user_player.player_info
			if data['keyid'] == 'prev':
				player_info.current_time = 1
				new_pos = True
			if data['keyid'] == 'minus10':
				player_info.current_time -= 10*60
				if player_info.current_time < 0:
					player_info.current_time = 1
				new_pos = True
			if data['keyid'] == 'play':
				player_info.play = not player_info.play
				if player_info.play:
					self.resume_play(user_name, user_player.device_friendly_name)
				else:
					self.pause_play(user_name, user_player.device_friendly_name)
			if data['keyid'] == 'plus10':
				if player_info.current_time + 10*60 < player_info.duration:
					player_info.current_time += 10*60
					new_pos = True
			if data['keyid'] == 'next':
				player_info.current_time = player_info.duration
				player_info.play = False
				new_pos = True
			if new_pos:
				self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_SETPOS, {
					'device_friendly_name': user_player.device_friendly_name, 'pos': player_info.current_time})

	def player_save_state(self, user_name):
		if user_name in self.players:
			user_player = self.players[user_name]
			player_info = user_player.player_info
			print('-------------------  Save State Request -------------')
			self.modref.message_handler.queue_event(user_name, defaults.PLAYER_SAVE_STATE_REQUEST, {
				'movie': user_player.movie, 'player_info': player_info})

	def refresh_app_movie_info(self, user_name):
		if user_name in self.players:
			user_player = self.players[user_name]
			movie=user_player.movie
			self.send_app_movie_info( user_name, movie)


	def handle_device_play_status(self, queue_event):
		try:
			cast_info = queue_event.data.cast_info
			# msg comes from device, so does not have a valid user name
			for user_name, user_player in self.players.items():  # does the user has a player?
				player_info = user_player.player_info
				if user_player.device_friendly_name == cast_info['device_friendly_name']:
					player_info.play = cast_info['play']
					player_info.current_time = cast_info['current_time']
					player_info.duration = cast_info['duration']
					player_info.volume = cast_info['volume']*100
					if cast_info['state_change']:
						print('-------------------  Save State Request -------------')
						self.player_save_state(user_name)
						#self.modref.message_handler.queue_event(user_name, defaults.PLAYER_SAVE_STATE_REQUEST, {
						#	'movie': user_player.movie, 'player_info': player_info})
					self.send_player_status(user_name, player_info)
		except:
			pass

	def send_player_status(self, user_name, player_info):
		self.modref.message_handler.queue_event(user_name, defaults.MSG_SOCKET_MSG, {
			'type': 'app_player_pos', 'config': player_info.__dict__})
		print(player_info.__dict__)

	def send_player_devices(self, user, devices, movie_uri):
		# we set the device info
		data = {
			'actual_device': '',
			'devices': devices,
			'movie_uri': movie_uri
		}
		self.modref.message_handler.queue_event(user, defaults.MSG_SOCKET_MSG, {
			'type': defaults.MSG_SOCKET_QUERY_FEASIBLE_DEVICES_ANSWER, 'config': data})

	def _run(self):
		''' starts the server
		'''
		while self.runFlag:
			time.sleep(1)

	def _stop(self):
		self.runFlag = False
