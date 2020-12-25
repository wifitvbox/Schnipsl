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
from urllib.parse import urlparse, urlunparse

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
	plugin_id = 'satepg'
	plugin_names = ['SAT EPG']

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
		self.origin_dir = os.path.dirname(__file__)
		self.config = JsonStorage(os.path.join(
			self.origin_dir, "config.json"), {
				'epgloops':1,
				'epgtimeout':60,
				'stream_source':'SatIP Live'
			}
		)
		self.stream_source=self.config.read('stream_source') # this defines who is the real data provider for the entries found in the EPG data

		self.epgbuffer_file_name = os.path.join(self.origin_dir, "epgbuffer.ts")

		self.process=None
		self.epg_storage = JsonStorage(os.path.join(
			self.origin_dir, "epgdata.json"), {'epgdata':{}})
		self.all_EPG_Data = self.epg_storage.read('epgdata')
		self.providers = set()
		self.categories = set()
		self.movies = {}
		self.timeline = {}
		self.lock=Lock()

	def event_listener(self, queue_event):
		''' react on events
		'''
		#print("event handler", self.plugin_id, queue_event.type, queue_event.user)
		if queue_event.type == defaults.STREAM_REQUEST_PLAY_LIST:
			self.stream_answer_play_list(queue_event)
		return queue_event  # dont forget the  event for further pocessing...

	def query_handler(self, queue_event, max_result_count):
		''' answers with list[] of results
		'''
		# print("query handler", self.plugin_id, queue_event.type,  queue_event.user, max_result_count)
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

					# now we need to do a dirty trick, because in our movies the entries are not store be the correct plugin name,
					# but the real data source instead, which is slighty confusing,,
					plugin_name=self.stream_source
					if plugin_name in self.movies:  # are there any movies stored for this plugin?
						with self.lock:
							for movie in self.movies[plugin_name].values():
								if movie.provider in queue_event.params['select_provider_values']:
									if titles or description_regexs: # in case any search criteria is given
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
										movie_info=MovieInfo.movie_to_movie_info(movie,'')
										movie_info['recordable']=True
										res.append(movie_info)
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
		new_epg_loaded=False
		actual_time=time.time()
		for provider in self.all_EPG_Data:
			if self.all_EPG_Data[provider]['requested']:
				if self.all_EPG_Data[provider]['lastmodified']<actual_time-60*60 or not self.all_EPG_Data[provider]['epg_data']:
					epg_details = self.get_epg_from_linvdr(
						provider,self.all_EPG_Data[provider]['url'])
					if epg_details:
						new_epg_loaded=True
						self.all_EPG_Data[provider]['lastmodified'] = time.time()
						self.all_EPG_Data[provider]['requested']=False
						for start_time, movie_info in epg_details.items():
							# refresh or add data
							self.all_EPG_Data[provider]['epg_data'][start_time] = movie_info
				movie_infos_to_delete=[]
				for start_time, movie_info in self.all_EPG_Data[provider]['epg_data'].items():
					if int(start_time) + movie_info['duration']<actual_time - 60*60: # the movie ended at least one hour ago
						movie_infos_to_delete.append(start_time)
				for start_time in movie_infos_to_delete:
					del(self.all_EPG_Data[provider]['epg_data'][start_time])
					new_epg_loaded=True
		if self.providers and not new_epg_loaded: # if this is not the first call (self.provides contains already data),but no new epg data
			return
		self.epg_storage.write('epgdata',self.all_EPG_Data)

		# refill the internal lists
		self.providers = set()
		self.categories = set()
		# we'll use the name of the stream source plugin instead the name of the EPG plugin itself
		# plugin_name = self.plugin_names[0]
		plugin_name = self.stream_source
		if not plugin_name in self.movies: 
			self.movies[plugin_name] = {}
		for provider, movie_data in self.all_EPG_Data.items():
			self.providers.add(provider)
			self.timeline[provider] = []
			for movie_info in movie_data['epg_data'].values():
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
		# reduce the pids to the ones containing SDT (0x11) and EIT (0x12)
		print('original URL:',url)
		url_st = urlparse(url)
		queries = url_st.query
		new_queries = ""
		if queries:
			for eq in queries.split("&"):
				key = eq.split("=")[0]
				value = eq.split("=")[1]
				if key == 'pids':
					value = "0,17,18"
				new_queries += key + "=" + value + "&"
		new_queries = new_queries.strip("&")
		url = urlunparse((
			url_st.scheme,
			url_st.netloc,
			url_st.path,
			url_st.params,
			new_queries,
			url_st.fragment,
		))



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
				result = {}
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
					movie_info['recordable']=True
					result[start]=movie_info
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
		else:
			self.all_EPG_Data[provider]['requested']=True
		time_stamp = time.time()
		try:
			epg_list =[]
			if provider in self.timeline:
				epg_list = self.timeline[provider]
			nr_of_entries = len(epg_list)
			i = 0
			while i < nr_of_entries and time_stamp > int(epg_list[i].timestamp):
				i += 1
			if i < nr_of_entries and i>0 and time_stamp <  int(epg_list[i-1].timestamp)+int(epg_list[i-1].movie_info['duration']):  # we found an entry
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
				combined_movie_info['recordable']=True
			else:
				combined_movie_info=MovieInfo(
					uri=':'.join([self.stream_source,provider,'0']),
					title='-',
					category='',
					provider=provider,
					timestamp=time_stamp,
					duration=0,  # 
					description='',
					query=None
				)
				combined_movie_info['recordable']=False

			self.modref.message_handler.queue_event(None, defaults.STREAM_ANSWER_PLAY_LIST, {'uri': queue_event.data['uri'],'movie_info':combined_movie_info})
		except Exception as e:
			print('unknown provider', provider, str(e))

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
