#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Standard module
from jsonstorage import JsonStorage
from messagehandler import Query
from classes import MovieInfo
from classes import Movie
import defaults
from splthread import SplThread
import sys
import os
import json
from base64 import b64encode
from threading import Timer , Lock
import time
import datetime
import calendar
import subprocess


from pprint import pprint

import re


# Non standard modules (install with pip)


ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../../../common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))

ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../.."))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))


# own local modules


class SplPlugin(SplThread):
	plugin_id = 'linvdrepg'
	plugin_names = ['LINVDR EPG']

	def __init__(self, modref):
		''' creates the object
		'''
		self.modref = modref

		super().__init__(modref.message_handler, self)
		modref.message_handler.add_event_handler(
			self.plugin_id, 0, self.event_listener)
		modref.message_handler.add_query_handler(
			self.plugin_id, 0, self.query_handler)
		self.runFlag = True

		# plugin specific stuff
		self.stream_source='LinVDR Live'
		self.origin_dir = os.path.dirname(__file__)
		self.config = JsonStorage(os.path.join(
			self.origin_dir, "config.json"), {'epgloops':1, 'epgtimeout':60})

		self.epgbuffer_file_name = os.path.join(self.origin_dir, "epgbuffer.ts")

		self.process=None
		self.all_EPG_Data = {}
		self.providers = set()
		self.categories = set()
		self.movies = {}
		self.timeline = {}
		self.lock=Lock()


	def event_listener(self, queue_event):
		''' react on events
		'''
		#print("xmltvepg event handler", queue_event.type, queue_event.user)
		if queue_event.type == defaults.STREAM_REQUEST_PLAY_LIST:
			self.stream_answer_play_list(queue_event)
			return None  # no further processing needed
		return queue_event  # dont forget the  event for further pocessing...

	def query_handler(self, queue_event, max_result_count):
		''' answers with list[] of results
		'''
		print("linvdrepg query handler", queue_event.type,
			  queue_event.user, max_result_count)
		if queue_event.type == defaults.QUERY_AVAILABLE_SOURCES:
			return self.plugin_names
		if queue_event.type == defaults.QUERY_AVAILABLE_PROVIDERS:
			res = []
			for plugin_name in self.plugin_names:
				# this plugin is one of the wanted
				if plugin_name in queue_event.params['select_source_values']:
					if plugin_name == self.plugin_names[0]:
						for provider in self.providers:
							if max_result_count > 0:
								res.append(provider)
								max_result_count -= 1
							else:
								return res  # maximal number of results reached
			return res
		if queue_event.type == defaults.QUERY_AVAILABLE_CATEGORIES:
			res = []
			for plugin_name in self.plugin_names:
				# this plugin is one of the wanted
				if plugin_name in queue_event.params['select_source_values']:
					for category in self.categories:
						if max_result_count > 0:
							res.append(category)
							max_result_count -= 1
						else:
							return res  # maximal number of results reached
			return res
		if queue_event.type == defaults.QUERY_MOVIE_ID:
			elements = queue_event.params.split(':')
			try:
				return [self.movies[elements[0]][queue_event.params]]
			except:
				return []
		if queue_event.type == defaults.QUERY_AVAILABLE_MOVIES:
			res = []
			titles = queue_event.params['select_title'].split()
			# descriptions=queue_event.params['select_description'].split()
			description_regexs = [re.compile(r'\b{}\b'.format(
				description), re.IGNORECASE) for description in queue_event.params['select_description'].split()]
			for plugin_name in self.plugin_names:
				# this plugin is one of the wanted
				if plugin_name in queue_event.params['select_source_values']:
					if plugin_name in self.movies:  # are there any movies stored for this plugin?
						for movie in self.movies[plugin_name].values():
							if movie.provider in queue_event.params['select_provider_values']:
								if titles:
									found = False
									for title in titles:
										if title.lower() in movie.title.lower():
											found = True
										if title.lower() in movie.category.lower():
											found = True
									if not found:
										continue
								if description_regexs:
									found = False
									for description_regex in description_regexs:
										if re.search(description_regex, movie.description):
											found = True
									if not found:
										continue

								if max_result_count > 0:
									res.append(
										MovieInfo.movie_to_movie_info(movie, ''))
									max_result_count -= 1
								else:
									return res  # maximal number of results reached
			return res
		return[]

	def _run(self):
		''' starts the server
		'''
		tick = 0
		while self.runFlag:
			with self.lock:
				self.check_for_updates()
			time.sleep(10)

	def _stop(self):
		self.runFlag = False

	# ------ plugin specific routines

	def getAbsolutePath(self, file_name):
		return os.path.join(self.origin_dir, file_name)

	def check_for_updates(self):
		# check for updates:
		for provider in self.all_EPG_Data:
			if self.all_EPG_Data[provider]['requested']:
				if self.all_EPG_Data[provider]['lastmodified']<time.time()-60*60:
						epg_details = self.get_epg_from_linvdr(
							provider,self.all_EPG_Data[provider]['url'])
						if epg_details:
							self.all_EPG_Data[provider]['epg_data'] = epg_details
							self.all_EPG_Data[provider]['lastmodified'] = time.time()
							self.all_EPG_Data[provider]['requested']=False

		# refill the internal lists
		self.providers = set()
		self.categories = set()
		# we'll use the name of the stream source plugin instead the name of the EPG plugin itself
		# plugin_name = self.plugin_names[0]
		plugin_name = self.stream_source
		if not plugin_name in self.movies:  # this is an indicator that the epg was loaded from disk and not updated from xmltv.se, so we need to fill a few structures
			self.movies[plugin_name] = {}
		for provider, movie_data in self.all_EPG_Data.items():
			self.providers.add(provider)
			self.timeline[provider] = []
			for movie_info in movie_data['epg_data']:
				self.timeline[provider].append(type('', (object,), {
												'timestamp': movie_info['timestamp'], 'movie_info': movie_info})())
				self.movies[plugin_name][movie_info['uri']] = Movie(
					source=plugin_name,
					source_type=defaults.MOVIE_TYPE_STREAM,
					provider=provider,
					category=movie_info['category'],
					title=movie_info['title'],
					timestamp=movie_info['timestamp'],
					duration=movie_info['duration'],
					description=movie_info['description'],
					url=movie_data['url']
				)
				self.categories.add(movie_info['category'])
		for epg_list in self.timeline.values():
			epg_list.sort(key=self.get_timestamp)

	def search_channel_info(self, channel_epg_name):
		channels_info = self.channels_info.read('channels_info')
		if channels_info:
			for channel_info in channels_info:
				if channel_info['channel_epg_name'] == channel_epg_name:
					return channel_info

	def get_epg_from_linvdr(self, provider,url):
		'''
./epg_grap.sh "http://192.168.1.7:3000/S19.2E-1-1079-28006.ts" ZDF 1
		'''
		attr=[os.path.join(	self.origin_dir, 'epg_grap.sh') , url, provider , str(self.config.read('epgloops')), str(self.config.read('epgtimeout'))] # process arguments
		print ("epg_grap started",provider, url,repr(attr))
		try:
			self.process = subprocess.Popen(attr, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			cleaner = Timer(600, self.cleanProcess) # if epg_grap won't exit, try to terminate its process in 30 seconds
			cleaner.start()
			epg_out, err = self.process.communicate()
			#self.process.wait() # oops... not needed? harmless!
			cleaner.cancel()
			if err:
				print ("epg_grap ended with an error:\n%s" % ( err))
			else:
				print ("epg_grap' ended")
				epg_json_string=epg_out.decode()
				epg_json = json.loads(epg_json_string)
				result = []
				count = 0
				for json_movie in epg_json['details'].values():
					start = json_movie['unixTimeBegin']
					stop = json_movie['unixTimeEnd']
					if json_movie['title']:
						title = json_movie['title']+' - '+json_movie['name']
					else:
						title = json_movie['name']
					desc = json_movie['description']
					category =  ''
					count += 1

					# we'll use the name of the stream source plugin instead the name of the EPG plugin itself
					# plugin_name = self.plugin_names[0]
					plugin_name = self.stream_source
					self.providers.add(provider)
					self.categories.add(category)
					new_movie = Movie(
						source=plugin_name,
						source_type=defaults.MOVIE_TYPE_STREAM,
						provider=provider,
						category=category,
						title=title,
						timestamp=str(int(start)),
						duration=stop-start,
						description=desc,
						url=url
					)
					new_movie.add_stream('ts', '', url)
					if not plugin_name in self.movies:
						self.movies[plugin_name] = {}
					self.movies[plugin_name][new_movie.uri()] = new_movie
					movie_info = MovieInfo.movie_to_movie_info(new_movie, category)
					result.append(movie_info)
				print("epg loaded, {0} entries".format(count))
				return result
		except Exception as ex:
			print ("epg_grap could not be started. Error: %s" % (ex))
		return

	def get_timestamp(self, elem):
		'''helper function for the array sort function
		'''
		return elem.timestamp

	def string_to_timestamp(self, timestring):
		if timestring:
			# read https://stackoverflow.com/a/2956997 to understand why timegm() is used insted of mktime()!
			return calendar.timegm(datetime.datetime.strptime(timestring, "%Y%m%d%H%M%S %z").timetuple())
		else:
			return ''

	def stream_answer_play_list(self,queue_event):
		uri= queue_event.data['uri']
		uri_elements =uri.split(':')
		source=uri_elements[0]
		if source != self.stream_source:
			return queue_event
		provider = uri_elements[1]
		if not provider in self.all_EPG_Data:
			movie_info_list = self.modref.message_handler.query(
				Query(None, defaults.QUERY_MOVIE_ID, source+':'+provider+':0'))
			if movie_info_list:
				movie= movie_info_list[0]
				url=movie.url
				with self.lock:
					self.all_EPG_Data[provider]={
						'requested':True,
						'url':url,
						'epg_data' : {},
						'lastmodified' : 0
					}
		time_stamp = time.time()
		try:
			epg_list = self.timeline[provider]
			found = None
			nr_of_entries = len(epg_list)
			i = 0
			while i < nr_of_entries and time_stamp > int(epg_list[i].timestamp):
				i += 1
			if i < nr_of_entries and i>0:  # we found an entry
				first_movie_info=epg_list[i-1].movie_info
				second_movie_info=epg_list[i].movie_info
				combined_movie_info=MovieInfo(
					uri=first_movie_info['uri'],
					title=first_movie_info['title'],
					category=second_movie_info['title'],
					provider=first_movie_info['provider'],
					timestamp=second_movie_info['timestamp'],
					duration=0,  # 
					description=first_movie_info['description'],
					query=first_movie_info['query']
				)
				self.modref.message_handler.queue_event(None, defaults.STREAM_ANSWER_PLAY_LIST, {'uri': queue_event.data['uri'],'movie_info':combined_movie_info})
		except:
			print('unknown provider', provider)

	def cleanProcess(self):
		try:
			if not self.process==None:
				self.process.terminate()
			time.sleep(3)
			if not self.process==None:
				self.process.kill()
				print ("Curl had to be killed. R.I.P.")
			else:
				print ("Curl had to be terminated.")
		except:
			print ("Curl termination error, process might be running")
		if not self.process==None:
			print ("Curl: termination may have failed")
		self.running = 0
