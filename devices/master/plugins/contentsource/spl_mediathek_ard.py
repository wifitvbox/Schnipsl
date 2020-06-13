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
from pprint import pprint

# Non standard modules (install with pip)

# sudo apt install libyajl-dev
# sudo pip3 install jsonslicer

from jsonslicer import JsonSlicer

ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))
# own local modules

from classes import Source


class SplPlugin(SplThread):
	plugin_id='mediathek_ard'

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

		##### plugin specific stuff
		self.providers=set()
		self.sources={}

	def event_listener(self, queue_event):
		''' react on events
		'''
		print("mediathek_ard event handler", queue_event.type, queue_event.user)

	def query_handler(self, queue_event, max_result_count):
		''' answers with list[] of results
		'''
		print("mediathek_ard query handler", queue_event.type,
		      queue_event.user, max_result_count)
		if queue_event.type == defaults.QUERY_AVAILABLE_SOURCES:
			return ['Öffi Mediathek']
		return[]

	def _run(self):
		''' starts the server
		'''
		self.load_filmlist('')
		tick = 0
		while self.runFlag:
			time.sleep(1)

	def _stop(self):
		self.runFlag = False

	def load_filmlist(self, file_name):
		loader_remember_data={'provider':'','channel':''}
		with open('/home/steffen//Desktop/workcopies/schnipsl/Filmliste-akt') as data:
			for liste in JsonSlicer(data, ('X'), path_mode='map_keys'):
				self.add_film(liste[1],loader_remember_data)

		print("filmlist loaded")

	def add_film(self, data_array,loader_remember_data):
				# "Sender"	0,
				# "Thema" 	1,
				# "Titel"	2,
				# "Datum"	3,
				# "Zeit"	4,
				# "Dauer"	5,
				# "Größe [MB]"	6,
				# "Beschreibung"	7,
				# "Url"				8,
				# "Website"			9,
				# "Url Untertitel"	10,
				# "Url RTMP"		11,
				# "Url Klein"		12,
				# "Url RTMP Klein"	13,
				# "Url HD"			14,
				# "Url RTMP HD"		15,
				# "DatumL"			16,
				# "Url History"		17,
				# "Geo"				18,
				# "neu"				19
		provider=data_array[0]
		channel=data_array[1]
		if provider:
			loader_remember_data['provider']=provider
		else:
			provider=loader_remember_data['provider']
		if channel:
			loader_remember_data['channel']=channel
		else:
			channel=loader_remember_data['channel']

		self.providers.add(provider)
		new_source = Source(
			source=self.plugin_id,
			provider=provider,
			channel=channel,
			title=data_array[2],
			timestamp=data_array[16],
			duration=data_array[5],
			description=data_array[7],
			url=data_array[8]
		)
		new_source.add_stream('mp4','',data_array[8])
		self.sources[new_source.uri()]=new_source
