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
			device = queue_event.data['device']
			movie = queue_event.data['movie']
			movie_id = queue_event.data['movie_id']
			self.stop_play(device)
			self.start_play(queue_event.user, device, movie, movie_id)
		if queue_event.type == defaults.MSG_SOCKET_PLAYER_KEY:
			handle_keys(queue_event)
		return queue_event

	def query_handler(self, queue_event, max_result_count):
		''' answers with list[] of results
		'''
		print("playerhandler query handler", queue_event.type,
			  queue_event.user, max_result_count)
		return[]

	def start_play(self, user, device, movie, movie_id):
		self.players[user] = {'movie': movie, 'device': device, 'player_info':{
				'play': True,
				'position': 0,
				'volume': 3,
				'time':0,
				'playTime': '00:00',
				'remainingTime': '00:00',
				'total_secs':90*60
			}
		}
		self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_REQUEST, {
			'user': user, 'movie': movie, 'movie_id': movie_id, 'device': device})
		print('Start play for {0} {1} {2} {3}'.format(
			user, device, movie_id, movie.url))

	def stop_play(self, device):
		self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_STOP, {
			'device': device})
		print('Stop play for {0}'.format(device))
	
	def handle_keys(self, user, data):
		if self.players[user]:
			user_player=self.players[user]
		if queue_event.data['keyid'] == 'prev':
			user_player.play_time = 0
		if queue_event.data['keyid'] == 'minus10':
			user_player.play_time -= 10*60
			if user_player.play_time < 0:
				user_player.play_time = 0
		if queue_event.data['keyid'] == 'play':
			user_player.player_info['play'] = not user_player.player_info['play']
		if queue_event.data['keyid'] == 'plus10':
			user_player.play_time += 10*60
			if user_player.play_time > user_player.play_total_secs:
				user_player.play_time = user_player.play_total_secs
		if queue_event.data['keyid'] == 'next':
			user_player.play_time = user_player.play_total_secs
			user_player.player_info['play'] = False
		self.send_player_status(user,user_player)


	def _run(self):
		''' starts the server
		'''
		tick = 0
		while self.runFlag:
			time.sleep(0.2)
			tick += 1
			if tick > 4:
				tick = 0
				for user_name, user_data in self.players.items():
					player_info=user_data['player_info']
					if player_info['play']:
						player_info['time'] += 5
						if player_info['time'] < 0:
							player_info['time'] = 0
						if player_info['time'] > 90*60:
							player_info['time'] = 0
							player_info['play'] = False
						self.send_player_status(user_name, player_info)

	def send_player_status(self,user_name, player_info):
		player_info['position'] = player_info['time'] * \
			100 // player_info['total_secs']
		player_info['playTime'] = '{:02d}:{:02d}'.format(
			player_info['time']//60, player_info['time'] % 60)
		player_info['remainingTime'] = '{:02d}:{:02d}'.format(
			(player_info['total_secs']-player_info['time'])//60, (player_info['total_secs']-player_info['time']) % 60)
		self.modref.message_handler.queue_event(user_name, defaults.MSG_SOCKET_MSG, {
			'type': 'app_player_pos', 'config': player_info})


	def _stop(self):
		self.runFlag = False
