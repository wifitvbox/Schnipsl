#!/usr/bin/env python
# -*- coding: utf-8 -*-

from HTTPWebSocketsHandler import HTTPWebSocketsHandler
'''
credits:
combined http(s) and websocket server copied from
	https://github.com/PyOCL/httpwebsockethandler
	The MIT License (MIT)
	Copyright (c) 2015 Seven Watt

'''

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
from pprint import pprint

# Non standard modules (install with pip)

from socketserver import ThreadingMixIn
from http.server import HTTPServer


# own local modules

from splthread import SplThread
import defaults


class Simulator(SplThread):

	def __init__(self, modref):
		''' creates the simulator
		'''
		self.modref = modref

		super().__init__(modref.message_handler, self)
		modref.message_handler.add_handler('simulator', 0, self.event_listener)
		self.runFlag = True
		self.play_time = 0
		self.play_total_secs = 90*60
		self.player_info = {
			'play': True,
			'position': 0,
			'volume': 3,
			'playTime': '00:00',
			'remainingTime': '00:00'
		}

	def event_listener(self, queue_event):
		''' try to send simulated answers
		'''
		print("simulator event handler", queue_event.type, queue_event.user)
		if queue_event.type == '_join':
			if queue_event:
				data = [
					{
						'icon': 'mdi-play-pause',
						'iconClass': 'blue white--text',
						'title': 'Steffen war hier',
						'subtitle': 'Jan 20, 2014'
					},
					{
						'icon': 'mdi-clock',
						'iconClass': 'amber white--text',
						'title': 'Blub',
						'subtitle': 'Jan 10, 2014'
					}
				]
				new_event = copy.copy(queue_event)
				new_event.type = defaults.MSG_SOCKET_MSG
				new_event.data = {'type': 'home_data', 'config': data}
				self.modref.message_handler.queue_event_obj(new_event)

		if queue_event.type == 'player_key':
			if queue_event.data['keyid'] == 'prev':
				self.play_time = 0
			if queue_event.data['keyid'] == 'minus10':
				self.play_time -= 10*60
				if self.play_time < 0:
					self.play_time = 0
			if queue_event.data['keyid'] == 'play':
				self.player_info['play'] = not self.player_info['play']
			if queue_event.data['keyid'] == 'plus10':
				self.play_time += 10*60
				if self.play_time > self.play_total_secs:
					self.play_time = self.play_total_secs
			if queue_event.data['keyid'] == 'next':
				self.play_time = self.play_total_secs
				self.player_info['play'] = False
			self.send_player_status()

	def send_player_status(self):
		self.player_info['position'] = self.play_time * \
			100 // self.play_total_secs
		self.player_info['playTime'] = '{:02d}:{:02d}'.format(
			self.play_time//60, self.play_time % 60)
		self.player_info['remainingTime'] = '{:02d}:{:02d}'.format(
			(self.play_total_secs-self.play_time)//60, (self.play_total_secs-self.play_time) % 60)
		self.modref.message_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
			'type': 'app_player_pos', 'config': self.player_info})

	def _run(self):
		''' starts the server
		'''
		tick = 0
		while self.runFlag:
			time.sleep(1)
			tick += 1
			if tick > 4:
				tick = 0
				if self.player_info['play']:
					self.play_time += 5
					if self.play_time < 0:
						self.play_time = 0
					if self.play_time > 90*60:
						self.play_time = 0
						self.player_info['play'] = False
					self.send_player_status()

	def _stop(self):
		self.runFlag = False
