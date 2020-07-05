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

from messagehandler import Query
from classes import MovieInfo
from classes import Movie
import defaults
from splthread import SplThread


class SplPlugin(SplThread):
	plugin_id='mediathek_ard'
	plugin_names=['Öffi Mediathek','LiveTV']

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
		self.movies={}

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
			return self.plugin_names
		if queue_event.type == defaults.QUERY_AVAILABLE_PROVIDERS:
			res=[]
			for plugin_name in self.plugin_names:
				if plugin_name  in queue_event.params['select_source_values']: # this plugin is one of the wanted
					for provider in self.providers:
						if max_result_count>0:
							res.append(provider)
							max_result_count-=1
						else:
							return res # maximal number of results reached
			return res
		if queue_event.type == defaults.QUERY_AVAILABLE_CATEGORIES:
			# just do nothing, the mediathek does not have categories
			pass
		if queue_event.type == defaults.QUERY_MOVIE_ID:
			elements=queue_event.params.split(':')
			try:
				return [self.movies[elements[0]][queue_event.params]]
			except:
				return []
		if queue_event.type == defaults.QUERY_AVAILABLE_MOVIES:
			res=[]
			titles=queue_event.params['select_title'].split()
			descriptions=queue_event.params['select_description'].split()
			for plugin_name in self.plugin_names:
				if plugin_name in queue_event.params['select_source_values']: # this plugin is one of the wanted
					for movie in self.movies[plugin_name].values():
						if movie.provider in queue_event.params['select_provider_values']:
							if titles:
								found=False
								for title in titles:
									if title.lower() in movie.title.lower():
										found=True
									if title.lower() in movie.category.lower():
										found=True
								if not found:
									continue
							if descriptions:
								found=False
								for description in descriptions:
									if description.lower() in movie.description.lower():
										found=True
								if not found:
									continue
								

							if max_result_count>0:
								res.append(MovieInfo.movie_to_movie_info(movie,'','0%'))
								max_result_count-=1
							else:
								return res # maximal number of results reached
			return res
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
		loader_remember_data={'provider':'','category':''}
		with open('/home/steffen//Desktop/workcopies/schnipsl/Filmliste-akt') as data:
			for liste in JsonSlicer(data, ('X'), path_mode='map_keys'):
				data_array=liste[1]
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
				category=data_array[1]
				if provider:
					loader_remember_data['provider']=provider
				else:
					provider=loader_remember_data['provider']
				if category:
					loader_remember_data['category']=category
				else:
					category=loader_remember_data['category']

				self.providers.add(provider)
				new_movie = Movie(
					source=self.plugin_names[0],
					provider=provider,
					category=category,
					title=data_array[2],
					timestamp=data_array[16],
					duration=data_array[5],
					description=data_array[7],
					url=data_array[8]
				)
				new_movie.add_stream('mp4','',data_array[8])
				plugin_name=self.plugin_names[0]
				if not plugin_name in self.movies:
					self.movies[plugin_name]={}
				self.movies[plugin_name][new_movie.uri()]=new_movie


		print("filmlist loaded")
