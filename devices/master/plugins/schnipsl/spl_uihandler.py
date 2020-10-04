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

ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))
# own local modules


class SplPlugin(SplThread):
	plugin_id = 'simulator'
	plugin_names = ['Plugin Simulator']

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
		self.play_time = 0
		self.play_total_secs = 90*60
		self.player_info = {
			'play': True,
			'position': 0,
			'volume': 3,
			'playTime': '00:00',
			'remainingTime': '00:00'
		}
		self.movielist = self.modref.store.read_users_value('movielist', {})

	def event_listener(self, queue_event):
		''' try to send simulated answers
		'''
		#print("simulator event handler", queue_event.type, queue_event.user)
		if queue_event.type == '_join':
			# send the movie list
			self.send_home_movie_list(queue_event)
		if queue_event.type == defaults.MSG_SOCKET_EDIT_DELETE_REQUEST:
			movie_list_uuid = queue_event.data['uuid']
			if movie_list_uuid in self.movielist:  # does the entry uuid exist
				movie_list_entry = self.movielist[movie_list_uuid]
				# is the user client of this entry?
				if queue_event.user in movie_list_entry['clients']:
					del(movie_list_entry['clients'][queue_event.user])
				# are there no more clients left?
				if not movie_list_entry['clients']:
					# remove the whole entry
					del (self.movielist[movie_list_uuid])
				self.send_home_movie_list(queue_event)
				self.modref.store.write_users_value(
					'movielist', self.movielist)
		if queue_event.type == defaults.MSG_SOCKET_SELECT_PLAYER_DEVICE:
				# starts to play movie on device
			print("plays schnipsl {0} on device ".format(
				queue_event.data['movie_uri']))
			movie_info_list = self.modref.message_handler.query(
				Query(queue_event.user, defaults.QUERY_MOVIE_ID, queue_event.data['movie_uri']))
			if movie_info_list:
				uuid = self.get_movielist_uuid_by_movie_uri(
					queue_event.user, queue_event.data['movie_uri'])
				if uuid:  # movie is in movie_list, so it has a current_time time
					current_time = self.movielist[uuid]['clients'][queue_event.user]['current_time']
					self.modref.message_handler.queue_event(queue_event.user, defaults.PLAYER_PLAY_REQUEST, {
						'user': queue_event.user, 'current_time': current_time, 'movie': movie_info_list[0], 'movie_uri': queue_event.data['movie_uri'], 'device': queue_event.data['timer_dev']})
		if queue_event.type == defaults.MSG_SOCKET_PLAYER_TIME:
			self.play_time = queue_event.data['timer_pos'] * \
				self.play_total_secs//100
		if queue_event.type == defaults.MSG_SOCKET_HOME_PLAY_REQUEST:
			movie_uri = queue_event.data['uri']

			movie_info_list = self.modref.message_handler.query(
				Query(queue_event.user, defaults.QUERY_MOVIE_ID, movie_uri))
			if movie_info_list:
				movie_list_uuid = self.get_movielist_uuid_by_movie_uri(
					queue_event.user, movie_uri)
				if movie_list_uuid:  # movie is in movie_list, so it has a current_time time

					current_time = self.movielist[movie_list_uuid]['clients'][queue_event.user]['current_time']
					self.modref.message_handler.queue_event(queue_event.user, defaults.PLAYER_PLAY_REQUEST_WITHOUT_DEVICE, {
						'user': queue_event.user, 'current_time': current_time, 'movie': movie_info_list[0], 'movie_uri': movie_uri})
		if queue_event.type == defaults.MSG_SOCKET_EDIT_PLAY_ADD_REQUEST:
			self.update_movie_list(queue_event)
		if queue_event.type == defaults.MSG_SOCKET_EDIT_PLAY_REQUEST:
			movie_list_uuid, movie_uri = self.update_movie_list(queue_event)
			if movie_list_uuid:
				movie_info_list = self.modref.message_handler.query(
					Query(queue_event.user, defaults.QUERY_MOVIE_ID, movie_uri))
				if movie_info_list:

					current_time = self.movielist[movie_list_uuid]['clients'][queue_event.user]['current_time']
					self.modref.message_handler.queue_event(queue_event.user, defaults.PLAYER_PLAY_REQUEST_WITHOUT_DEVICE, {
						'user': queue_event.user, 'current_time': current_time, 'movie': movie_info_list[0], 'movie_uri': queue_event.data['movie_uri']})
		if queue_event.type == defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_SOURCES:
			available_items = self.modref.message_handler.query(
				Query(queue_event.user, defaults.QUERY_AVAILABLE_SOURCES, None))
			available_items.sort()
			data = {
				'select_items': available_items,
				'select_values': self.filter_select_values(available_items, queue_event.data['select_source_values'])
			}
			self.modref.message_handler.queue_event(queue_event.user, defaults.MSG_SOCKET_MSG, {
				'type': defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_SOURCES_ANSWER, 'config': data})
		if queue_event.type == defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_PROVIDERS:
			available_items = self.modref.message_handler.query(
				Query(queue_event.user, defaults.QUERY_AVAILABLE_PROVIDERS, queue_event.data))
			available_items.sort()
			data = {
				'select_items': available_items,
				'select_values': self.filter_select_values(available_items, queue_event.data['select_provider_values'])
			}
			self.modref.message_handler.queue_event(queue_event.user, defaults.MSG_SOCKET_MSG, {
				'type': defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_PROVIDERS_ANSWER, 'config': data})
		if queue_event.type == defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_CATEGORIES:
			available_items = self.modref.message_handler.query(
				Query(queue_event.user, defaults.QUERY_AVAILABLE_CATEGORIES, queue_event.data))
			available_items.sort()
			data = {
				'select_items': available_items,
				'select_values': self.filter_select_values(available_items, queue_event.data['select_category_values'])
			}
			self.modref.message_handler.queue_event(queue_event.user, defaults.MSG_SOCKET_MSG, {
				'type': defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_CATEGORIES_ANSWER, 'config': data})
		if queue_event.type == defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_MOVIES:
			query_start_page = 0
			if 'query_start_page' in queue_event.data:
				query_start_page = queue_event.data['query_start_page']
			movie_info_list = self.modref.message_handler.query(
				Query(queue_event.user, defaults.QUERY_AVAILABLE_MOVIES, queue_event.data))
			if query_start_page < 1:
				prev_page = -1
			else:
				prev_page = query_start_page-1
			# indicates that there are some more entries
			if len(movie_info_list) > defaults.MAX_QUERY_SIZE:
				next_page = query_start_page+1
			else:
				next_page = -1
			self.modref.message_handler.queue_event(queue_event.user, defaults.MSG_SOCKET_MSG, {
				'type': defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_MOVIES_ANSWER, 'config': {'movie_info_list': movie_info_list, 'prev_page': prev_page, 'query_start_page': query_start_page, 'next_page': next_page}})
		if queue_event.type == defaults.PLAYER_SAVE_STATE_REQUEST:
			movie = queue_event.data['movie']
			user = queue_event.user
			player_info = queue_event.data['player_info']
			self.handle_player_save_state_request(user, movie, player_info)
		if queue_event.type == defaults.STREAM_ANSWER_PLAY_LIST:
			movie_uri=queue_event.data['uri']
			movie_info=queue_event.data['movie_info']
			for uuid, search_movie in self.movielist.items():
				if not search_movie['movie_info']['uri'] == movie_uri:
					continue
				for user_name in search_movie['clients']:
					self.update_live_movie_clip( user_name, uuid,movie_info)
		# for further pocessing, do not forget to return the queue event
		return queue_event

	def query_handler(self, queue_event, max_result_count):
		''' try to send simulated answers
		'''
		print("simulator query handler", queue_event.type,
			  queue_event.user, max_result_count)
		return[]

	def _run(self):
		''' starts the server
		'''
		while self.runFlag:
			act_secs=int(time.time())
			# time until the next full minute
			remaining_secs=act_secs % 60
			if remaining_secs:
				time.sleep(remaining_secs)
			self.request_stream_playlist()

	def _stop(self):
		self.runFlag = False

	#------ plugin specific routines

	def prepare_movie_list(self, user_name):
		''' prepares the list of the user_name movies to display on the client in the main window
		'''
		res = {'templates': [], 'records': [], 'streams': [], 'timers': []}
		for uuid, movie_list_item in self.movielist.items():
			if not user_name in movie_list_item['clients']:

				continue
			if movie_list_item['type'] == defaults.MOVIE_TYPE_TEMPLATE:
				res['templates'].append(
					{
						'uuid': uuid,
						'icon': 'mdi-magnify',
						'iconClass': 'red lighten-1 white--text',
						'query': movie_list_item['query'],
						'movie_info': movie_list_item['movie_info'],
						'current_time': ''
					}
				)
			if movie_list_item['type'] == defaults.MOVIE_TYPE_RECORD:
				user_current_time = str(
					movie_list_item['clients'][user_name]['current_time'])

				res['records'].append(
					{
						'uuid': uuid,
						'icon': 'mdi-play-pause',
						'iconClass': 'blue white--text',
						'query': movie_list_item['query'],
						'movie_info': movie_list_item['movie_info'],
						'current_time': user_current_time
					}
				)
			if movie_list_item['type'] == defaults.MOVIE_TYPE_STREAM:
				res['streams'].append(
					{
						'uuid': uuid,
						'icon': 'mdi-radio-tower',
						'iconClass': 'green lighten-1 white--text',
						'query': movie_list_item['query'],
						'movie_info': movie_list_item['movie_info'],
						'current_time': ''
					}
				)
			if movie_list_item['type'] == defaults.MOVIE_TYPE_TIMER:
				res['timers'].append(
					{
						'uuid': uuid,
						'icon': 'mdi-clock',
						'iconClass': 'amber white--text',
						'query': movie_list_item['query'],
						'movie_info': movie_list_item['movie_info'],
						'current_time': ''
					}
				)
		return res

	def update_movie_list(self, queue_event):
		'''
		'''

		# is it a quick search? Then update the quicksearch data first
		quick_search_name = queue_event.data['query']['name']
		if quick_search_name:
			quick_search_entry = None
			for movie_list_entry in self.movielist.values():
				if movie_list_entry['query'] and movie_list_entry['query']['name'].lower() == quick_search_name.lower() and queue_event.user in movie_list_entry['clients']:
					quick_search_entry = movie_list_entry
					break
			if not quick_search_entry:
				quick_search_entry = {
					'clients': {},
				}
				quick_search_entry['clients'][queue_event.user] = {
					'current_time': 0}
				# new entry, so it gets its own identifier
				quick_search_entry_id = str(uuid.uuid4())
				self.movielist[quick_search_entry_id] = quick_search_entry
			quick_search_entry['type'] = defaults.MOVIE_TYPE_TEMPLATE
			quick_search_entry['query'] = queue_event.data['query']
			quick_search_entry['movie_info'] = MovieInfo(
				'0',  # uuid
				quick_search_name,  # title
				'',  # category
				'',  # provider
				'',  # timestamp
				'',  # duration
				'',  # current_time
				''  # description
			)

		movie_list = self.modref.message_handler.query(
			Query(queue_event.user, defaults.QUERY_MOVIE_ID, queue_event.data['movie_uri']))
		if movie_list:
			# TODO
			# ist es ein Live- Movie? Dann wird es als Live- Schnipsl angehängt
			# ist es ein benamter Quick-Search? Gibt es ihn schon oder ist er neu?
			# ist ein normaler Stream?
			# ist es ein Record- Eintrag?
			movie_list_uuid = queue_event.data['uuid']
			# an existing entry was edited, and it was not a quicksearch
			if movie_list_uuid in self.movielist and not quick_search_name:
				print("Molist Eintrag existiert schon")
				movie_list_entry = self.movielist[movie_list_uuid]
			else:
				movie_list_entry = {

					'clients': {},

				}
				movie_list_entry['clients'][queue_event.user] = {
					'current_time': 0}
				# new entry, so it gets its own identifier
				movie_list_uuid = str(uuid.uuid4())
				self.movielist[movie_list_uuid] = movie_list_entry
			movie_list_entry['type'] = movie_list[0].source_type
			# we need to make a copy here, because in case of a new created quicksearch item the quicksearch query data and this normal item both points to the same query object,
			# which causes an error (name="") in the quicksearch item when we remove the name here...
			movie_list_entry['query'] = copy.copy(queue_event.data['query'])
			# as this is not a quicksearch entry anymore, we must make sure that it does not contain a
			# quicksearch name anymore
			movie_list_entry['query']['name'] = ''
			movie_list_entry['movie_info'] = MovieInfo(
				queue_event.data['movie_uri'],  # uuid
				movie_list[0].title,  # title
				movie_list[0].category,  # category
				movie_list[0].provider,  # provider
				movie_list[0].timestamp,  # timestamp
				movie_list[0].duration,  # duration
				movie_list[0].description  # description
			)

			self.modref.store.write_users_value('movielist', self.movielist)
			return movie_list_uuid, movie_list[0].uri()
		else:
			self.modref.store.write_users_value('movielist', self.movielist)
			return None

	def filter_select_values(self, value_list, actual_values):
		'''returns list of the values of actual_values, which are included in value list
		'''
		res = []
		for value in actual_values:
			if value in value_list:
				res.append(value)
		return res

	def update_single_movie_clip(self, user_name, movie_list_uuid):
		movie_list_item = self.movielist[movie_list_uuid]
		current_time = movie_list_item["clients"][user_name]['current_time']
		self.modref.message_handler.queue_event(user_name, defaults.MSG_SOCKET_MSG, {
			'type': defaults.MSG_SOCKET_HOME_MOVIE_INFO_UPDATE, 'config': {'uuid': movie_list_uuid, 'current_time': current_time, 'movie_info': movie_list_item['movie_info']}})

	def update_live_movie_clip(self, user_name, movie_list_uuid,live_music_info):
		current_time = live_music_info['duration']-int(time.time())+int(live_music_info['timestamp'])
		self.modref.message_handler.queue_event(user_name, defaults.MSG_SOCKET_MSG, {
			'type': defaults.MSG_SOCKET_HOME_MOVIE_INFO_UPDATE, 'config': {'uuid': movie_list_uuid, 'current_time': current_time, 'movie_info': live_music_info}})

	def send_home_movie_list(self, original_queue_event):
		new_event = copy.copy(original_queue_event)
		new_event.type = defaults.MSG_SOCKET_MSG
		new_event.data = {
			'type': defaults.MSG_SOCKET_HOME_MOVIE_INFO_LIST, 'config': self.prepare_movie_list(original_queue_event.user)}
		#print("new_event", new_event.data['config'])
		self.modref.message_handler.queue_event_obj(new_event)

	def get_movielist_uuid_by_movie_uri(self, user, movie_uri):
		for uuid, search_movie in self.movielist.items():
			if not search_movie['movie_info']['uri'] == movie_uri:
				continue
			if not user in search_movie['clients']:
				continue
			return uuid
		return None

	def handle_player_save_state_request(self, user, movie, player_info):
		movie_uri = movie.uri()
		uuid = self.get_movielist_uuid_by_movie_uri(user, movie_uri)
		if uuid:
			search_movie = self.movielist[uuid]
			search_movie['clients'][user]['current_time'] = player_info.current_time
			self.update_single_movie_clip(user, uuid)
			self.modref.store.write_users_value('movielist', self.movielist)

	def request_stream_playlist(self):
		for movie_list_item in self.movielist.values():
			if movie_list_item['type'] == defaults.MOVIE_TYPE_STREAM:
				self.modref.message_handler.queue_event(None, defaults.STREAM_REQUEST_PLAY_LIST, {'uri': movie_list_item['movie_info']['uri']})

