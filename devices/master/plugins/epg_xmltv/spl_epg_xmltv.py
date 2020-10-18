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
import threading
import ssl
import json
from base64 import b64encode
import argparse

import time
import datetime
import calendar

from io import StringIO
import threading
from pprint import pprint

import urllib
from urllib.request import urlopen, urlretrieve
from xml.etree.ElementTree import parse
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
	plugin_id = 'xmltvepg'
	plugin_names = ['XMLTV EPG', 'SAT Channels']

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
			self.origin_dir, "data.json"), {})
		self.channels_info = JsonStorage(os.path.join(
			self.origin_dir, "channels_info.json"), {})

		self.allChannels = set()
		self.providers = set()
		self.categories = set()
		self.movies = {}
		self.timeline = {}
		self.favorite_channels = ['daserste.de', 'einsextra.daserste.de',
								  'einsfestival.daserste.de', 'ndrhd.daserste.de', 'hd.zdf.de']

	def event_listener(self, queue_event):
		''' react on events
		'''
		#print("xmltvepg event handler", queue_event.type, queue_event.user)
		if queue_event.type == defaults.STREAM_REQUEST_PLAY_LIST:
			self.stream_answer_play_list(queue_event)
			return None  # no further processing needed
		return queue_event
		return queue_event  # dont forget the  event for further pocessing...

	def query_handler(self, queue_event, max_result_count):
		''' answers with list[] of results
		'''
		print("xmltvepg query handler", queue_event.type,
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
					if plugin_name == self.plugin_names[1]:
						for channel in self.allChannels:
							if max_result_count > 0:
								res.append(channel)
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
		self.load_filmlist('xmltv_datalist.xml.gz')
		tick = 0
		while self.runFlag:
			time.sleep(1)

	def _stop(self):
		self.runFlag = False

	# ------ plugin specific routines

	def getAbsolutePath(self, file_name):
		return os.path.join(self.origin_dir, file_name)

	def load_filmlist(self, file_name):
		origin_dir = os.path.dirname(__file__)
		file_name = os.path.join(origin_dir, file_name)
		update_list=None
		print(os.path.abspath(file_name))
		try:  # does the file exist at all already?
			xmltv_updates_time_stamp = os.path.getmtime(file_name)
		except:
			xmltv_updates_time_stamp = 0
		print("timestamp", xmltv_updates_time_stamp, time.time())
		if xmltv_updates_time_stamp < time.time() - 60*60*48:  # file is older as 48 hours
			print("Retrieve xmltv_updates list")
			try:
				urlretrieve(
					'https://xmltv.xmltv.se/datalist.xml.gz', file_name)
			except Exception as e:
				print('failed xmltv_updates download', str(e))
		try:
			with open(file_name, 'rb') as xmltv_updates_file_handle:
				update_list = parse(xmltv_updates_file_handle)
		except Exception as e:
			print('failed xmltv_updates read', str(e))
		epg_data = self.config.read('epg', {})
		collect_lastmodified = {}
		if update_list:
			for channel in update_list.iterfind('channel'):
				channel_id = channel.attrib['id']
				self.allChannels.add(channel_id)
				if channel_id in self.favorite_channels:
					if not channel_id in collect_lastmodified:
						collect_lastmodified[channel_id] = {}
					for datafor in channel.iterfind('datafor'):
						day_text = datafor.text
						last_modified = datafor.attrib['lastmodified']
						collect_lastmodified[channel_id][day_text] = last_modified
		# first we delete old, outdated dates
		for channel_id in list(epg_data):
			if not channel_id in collect_lastmodified:
				del(epg_data[channel_id])  # delete the whole channel
			else:
				for day_text in list(epg_data[channel_id]):
					if not day_text in collect_lastmodified[channel_id]:
						del(epg_data[channel_id][day_text])
		# check for updates:
		for channel_id in collect_lastmodified:
			print(channel_id)
			if not channel_id in epg_data:
				epg_data[channel_id] = {}
			for day_text in collect_lastmodified[channel_id]:
				try:
					if not day_text in epg_data[channel_id]:
						epg_details = self.load_from_xmltv(
							channel_id, day_text)
						epg_data[channel_id][day_text] = {
							'lastmodified': collect_lastmodified[channel_id][day_text], 'epg_data': epg_details}
						print('store', channel_id, day_text)
					else:
						if epg_data[channel_id][day_text]['lastmodified'] < collect_lastmodified[channel_id][day_text]:
							epg_details = self.load_from_xmltv(
								channel_id, day_text)
							epg_data[channel_id][day_text] = {
								'lastmodified': collect_lastmodified[channel_id][day_text], 'epg_data': epg_details}
							print("update epg for ", channel_id, day_text)
				except Exception as e:
					print('exception on load_from_xmltv',
						  channel_id, day_text, str(e))
		self.config.write('epg', epg_data, False)
		# refill the internal lists
		self.providers = set()
		self.categories = set()
		plugin_name = self.plugin_names[0]
		if not plugin_name in self.movies:  # this is an indicator that the epg was loaded from disk and not updated from xmltv.se, so we need to fill a few structures
			self.movies[plugin_name] = {}
		for provider, days in epg_data.items():
			self.providers.add(provider)
			self.timeline[provider] = []
			for movie_data in days.values():
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
						url=None
					)
					self.categories.add(movie_info['category'])
		for epg_list in self.timeline.values():
			epg_list.sort(key=self.get_timestamp)

	def get_attrib(self, xmlelement, identifier, default=None):
		'''
		reads a attribute fail-safe
		'''
		try:
			return xmlelement.attrib[identifier]
		except:
			return default

	def get_text(self, xmlelement, default=None):
		'''
		reads a element text fail-safe
		'''
		try:
			return xmlelement.text
		except:
			return default

	def search_channel_info(self, channel_epg_name):
		channels_info = self.channels_info.read('channels_info')
		if channels_info:
			for channel_info in channels_info:
				if channel_info['channel_epg_name'] == channel_epg_name:
					return channel_info

	def load_from_xmltv(self, channel_id, day_text):
		'''

		'''
		var_url = urlopen('https://xmltv.xmltv.se/' +
						  channel_id+'_'+day_text+'.xml')
		epg_xml = parse(var_url)
		result = []
		count = 0
		for programme in epg_xml.iterfind('programme'):
			provider = self.get_attrib(programme, 'channel')
			start = self.string_to_timestamp(
				self.get_attrib(programme, 'start'))
			stop = self.string_to_timestamp(self.get_attrib(programme, 'stop'))
			title = self.get_text(programme.find('title'), '')
			desc = self.get_text(programme.find('desc'), '')
			category = self.get_text(programme.find('category'), '')
			episode = programme.find('episode-num')
			episode_num = None
			channel_info = self.search_channel_info(provider)
			url = None
			media_type = None
			if channel_info:
				url = channel_info['url']
				media_type = channel_info['mediatype']
			if episode:
				num_system = self.get_attrib(episode, 'system')
				if num_system == 'xmltv_ns':
					episode_num = self.get_text(episode)

			count += 1

			plugin_name = self.plugin_names[0]
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
			new_movie.add_stream(media_type, '', url)
			if not plugin_name in self.movies:
				self.movies[plugin_name] = {}
			self.movies[plugin_name][new_movie.uri()] = new_movie
			movie_info = MovieInfo.movie_to_movie_info(new_movie, category)
			result.append(movie_info)
		print("epg loaded, {0} entries".format(count))
		return result

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
		uri_elements = queue_event.data['uri'].split(':')
		provider = uri_elements[1]
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
