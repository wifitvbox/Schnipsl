#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Standard module
from messagehandler import Query
from classes import MovieInfo
import defaults
from splthread import SplThread
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
import uuid
from pprint import pprint

# Non standard modules (install with pip)

import pychromecast
import zeroconf

# own local modules
ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))


class SplPlugin(SplThread):
	plugin_id='chromecast'
	plugin_names=['Chromecast']

	def __init__(self, modref):
		''' creates the plugin
		'''
		self.modref = modref

		super().__init__(modref.message_handler, self)
		modref.message_handler.add_event_handler(
		self.plugin_id, 0, self.event_listener)
		modref.message_handler.add_query_handler(
		self.plugin_id, 0, self.query_handler)
		self.runFlag = True

		##### plugin specific stuff
		self.chromecasts = {}


	def event_listener(self, queue_event):
		if queue_event.type == defaults.MSG_SOCKET_EDIT_DELETE_REQUEST:
			pass
		# for further pocessing, do not forget to return the queue event
		return queue_event

	def query_handler(self, queue_event, max_result_count):
		''' try to send simulated answers
		'''
		print("chromecast query handler", queue_event.type,
			  queue_event.user, max_result_count)
		if queue_event.type == defaults.QUERY_FEASIBLE_DEVICES:
			return ['TV Wohnzimmer-S', 'TV Küche-s', 'Chromecast Büro']
		return[]


	def _run(self):
		''' starts the server
		'''
		tick = 0
		while self.runFlag:
			time.sleep(1)


	def _stop(self):
		self.runFlag = False
