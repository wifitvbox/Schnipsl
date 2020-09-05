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
import lzma
import time
import urllib
from urllib.request import urlopen,urlretrieve
from xml.etree.ElementTree import parse
import re

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
			#descriptions=queue_event.params['select_description'].split()
			description_regexs=[re.compile (r'\b{}\b'.format(description),re.IGNORECASE) for description in queue_event.params['select_description'].split()]
			for plugin_name in self.plugin_names:
				if plugin_name in queue_event.params['select_source_values']: # this plugin is one of the wanted
					if plugin_name in self.movies: # are there any movies stored for this plugin?
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
								if description_regexs:
									found=False
									for description_regex in description_regexs:
										if re.search(description_regex, movie.description):
											found=True
									if not found:
										continue
									

								if max_result_count>0:
									res.append(MovieInfo.movie_to_movie_info(movie,''))
									max_result_count-=1
								else:
									return res # maximal number of results reached
			return res
		return[]

	def _run(self):
		''' starts the server
		'''
		self.load_filmlist(os.path.abspath('online_filmlist')) # BUG: we need to give a absolute path as the webserver will change the path suddenly later...
		tick = 0
		while self.runFlag:
			time.sleep(1)

	def _stop(self):
		self.runFlag = False

	def load_filmlist(self, file_name):
		print(os.path.abspath(file_name))
		try: # does the file exist at all already?
			filmlist_time_stamp= os.path.getmtime(file_name)
		except:
			filmlist_time_stamp=0
		print("timestamp",filmlist_time_stamp,time.time())
		if filmlist_time_stamp<time.time() - 60*60*48: # file is older as 48 hours
			print("Retrieve film list")
			try:
				var_url = urlopen('https://res.mediathekview.de/akt.xml')
				server_list = parse(var_url)
				print(server_list)
				url=None
				prio=999 # dummy start value
				for item in server_list.iterfind('Server'):
					this_prio = int(item.findtext('Prio'))
					if this_prio< prio: # filter for the server with the lowest prio
						prio=this_prio
						url = item.findtext('URL')
						print(url)
						print(prio)
						print()
				if url:
					try:
						urlretrieve(url,file_name+'.pack')
					except  Exception as e:
						print('failed filmlist download',str(e))
					try:
						with open(file_name,'wb') as unpack_file_handle:
							unpack_file_handle.write(lzma.open(file_name+'.pack').read())
					except  Exception as e:
						print('failed filmlist unpack',str(e))
				
			except  Exception as e:
				print('failed filmlist server list download')
		loader_remember_data={'provider':'','category':''}


		'''
		Bootstrap to read the filmlist:
		1. read the list of actual filmlist URLs from https://res.mediathekview.de/akt.xml
		'''


		#with open('/home/steffen//Desktop/workcopies/schnipsl/Filmliste-akt') as data:
		with open(file_name) as data:
			count=0
			for liste in JsonSlicer(data, ('X'), path_mode='map_keys'):
				count+=1
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
				if category=='Livestream':
					source_type=defaults.MOVIE_TYPE_STREAM
					plugin_name=self.plugin_names[1]
					provider=provider.replace('Livestream','').strip()
					#print("Livestream")
				else:
					plugin_name=self.plugin_names[0]
					source_type=defaults.MOVIE_TYPE_RECORD
				self.providers.add(provider)
				new_movie = Movie(
					source=plugin_name,
					source_type=source_type,
					provider=provider,
					category=category,
					title=data_array[2],
					timestamp=data_array[16],
					duration=data_array[5],
					description=data_array[7],
					url=data_array[8]
				)
				new_movie.add_stream('mp4','',data_array[8])
				if not plugin_name in self.movies:
					self.movies[plugin_name]={}
				self.movies[plugin_name][new_movie.uri()]=new_movie


		print("filmlist loaded, {0} entries",count)
