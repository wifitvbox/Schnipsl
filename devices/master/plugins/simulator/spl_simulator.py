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

	def __init__(self, modref):
		''' creates the simulator
		'''
		self.modref = modref

		super().__init__(modref.message_handler, self)
		modref.message_handler.add_event_handler(
			'simulator', 0, self.event_listener)
		modref.message_handler.add_query_handler(
			'simulator', 0, self.query_handler)
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
		self.movielist = {
			'1': {
				'type': 'template',
						'clients': {'uschi': {}, 'steffen': {}},
						'query': None,
						'movie_info': MovieInfo(
							'1',
							'Titel-S',
							'Typ',
							'Quelle',
							'Datum',
							'Dauer',
							'geschaut',
							'Lorem ipsum..'
						)
			},
			'2': {
				'type': 'template',
						'clients': {'uschi': {}},
						'query': None,
						'movie_info': MovieInfo(
							'2',
							'Titel-2-S',
							'Typ',
							'Quelle',
							'Datum',
							'Dauer',
							'geschaut',
							'Lorem ipsum..'
						)
			},
			'3': {
				'type': 'record',
						'clients': {'uschi': {}, 'steffen': {}},
						'query': None,
						'movie_info': MovieInfo(
							'3',
							'Titel-Record-S',
							'Typ',
							'Quelle',
							'Datum',
							'Dauer',
							'geschaut',
							'Lorem ipsum..'
						)
			},
			'4': {
				'type': 'stream',
						'clients': {'uschi': {}, 'steffen': {}},
						'query': None,
						'movie_info': MovieInfo(
							'4',
							'Titel-Stream-S',
							'Typ',
							'Quelle',
							'Datum',
							'Dauer',
							'geschaut',
							'Lorem ipsum..'
						)
			},
			'5': {
				'type': 'timer',
						'clients': {'uschi': {}, 'steffen': {}},
						'query': None,
						'movie_info': MovieInfo(
							'5',
							'Titel-Timer-S',
							'Typ',
							'Quelle',
							'Datum',
							'Dauer',
							'geschaut',
							'Lorem ipsum..'
						)
			}
		}

	def prepare_movie_list(self, user):
		''' prepares the list of the user movies to display on the client in the main window
		'''
		res = {'templates': [], 'records': [], 'streams': [], 'timers': []}
		for id, movie in self.movielist.items():
			if not user.name in movie['clients']:
				continue
			if movie['type'] == defaults.MOVIE_TYPE_TEMPLATE:
				res['templates'].append(
					{
						'id': id,
						'icon': 'mdi-magnify',
								'iconClass': 'red lighten-1 white--text',
								'query': movie['query'],
								'movie_info': movie['movie_info']
					}
				)
			if movie['type'] == defaults.MOVIE_TYPE_RECORD:
				res['records'].append(
					{
						'id': id,
						'icon': 'mdi-play-pause',
								'iconClass': 'blue white--text',
								'query': movie['query'],
								'movie_info': movie['movie_info']
					}
				)
			if movie['type'] == defaults.MOVIE_TYPE_STREAM:
				res['streams'].append(
					{
						'id': id,
						'icon': 'mdi-radio-tower',
								'iconClass': 'green lighten-1 white--text',
								'query': movie['query'],
								'movie_info': movie['movie_info']
					}
				)
			if movie['type'] == defaults.MOVIE_TYPE_TIMER:
				res['timers'].append(
					{
						'id': id,
						'icon': 'mdi-clock',
								'iconClass': 'amber white--text',
								'query': movie['query'],
								'movie_info': movie['movie_info']
					}
				)
		return res

	def event_listener(self, queue_event):
		''' try to send simulated answers
		'''
		#print("simulator event handler", queue_event.type, queue_event.user)
		if queue_event.type == '_join':
			# send the movie list
			self.send_home_movie_list(queue_event)
			self.update_single_movie_clip('1')
		if queue_event.type == defaults.MSG_SOCKET_EDIT_DELETE_REQUEST:
			movie_list_id=queue_event.data['edit_id']
			if movie_list_id in self.movielist: # does the entry id exist
				movie_list_entry=self.movielist[movie_list_id]
				if queue_event.user.name in movie_list_entry['clients']: # is the user client of this entry?
					del(movie_list_entry['clients'][queue_event.user.name])
				if not movie_list_entry['clients']: # are there no more clients left?
					del (self.movielist[movie_list_id]) # remove the whole entry
				self.send_home_movie_list(queue_event)
		if queue_event.type == defaults.MSG_SOCKET_SELECT_PLAYER_DEVICE:
				# request to play a movie on a device
				self.play_request(queue_event)

		if queue_event.type == defaults.MSG_SOCKET_PLAYER_KEY:
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
		if queue_event.type == defaults.MSG_SOCKET_PLAYER_TIME:
			self.play_time = queue_event.data['timer_pos'] * \
				self.play_total_secs//100
		if queue_event.type == defaults.MSG_SOCKET_HOME_PLAY_REQUEST:
			movie_id=queue_event.data['itemId']
			feasible_devices = self.modref.message_handler.query(Query(
				queue_event.user, defaults.QUERY_FEASIBLE_DEVICES, movie_id))
			self.send_player_devices(feasible_devices,movie_id)
		if queue_event.type == defaults.MSG_SOCKET_EDIT_PLAY_REQUEST:
			movie_list_id, movie_id = self.update_movie_list(queue_event)
			if movie_list_id:
				feasible_devices = self.modref.message_handler.query(Query(
					queue_event.user, defaults.QUERY_FEASIBLE_DEVICES, movie_id))
				self.send_player_devices(feasible_devices, movie_id)
		if queue_event.type == defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_SOURCES:
			available_items = self.modref.message_handler.query(
				Query(queue_event.user, defaults.QUERY_AVAILABLE_SOURCES, None))
			# we set the device info
			data = {
				'select_items': available_items,
				'select_values': self.filter_select_values(available_items, queue_event.data['select_source_values'])
			}
			self.modref.message_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
				'type': defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_SOURCES_ANSWER, 'config': data})

		if queue_event.type == defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_PROVIDERS:
			available_items = self.modref.message_handler.query(
				Query(queue_event.user, defaults.QUERY_AVAILABLE_PROVIDERS, queue_event.data))
			# we set the device info
			data = {
				'select_items': available_items,
				'select_values': self.filter_select_values(available_items, queue_event.data['select_provider_values'])
			}
			self.modref.message_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
				'type': defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_PROVIDERS_ANSWER, 'config': data})

		if queue_event.type == defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_CATEGORIES:
			available_items = self.modref.message_handler.query(
				Query(queue_event.user, defaults.QUERY_AVAILABLE_CATEGORIES, queue_event.data))
			# we set the device info
			data = {
				'select_items': available_items,
				'select_values': self.filter_select_values(available_items, queue_event.data['select_category_values'])
			}
			self.modref.message_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
				'type': defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_CATEGORIES_ANSWER, 'config': data})

		if queue_event.type == defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_MOVIES:
			movie_list = self.modref.message_handler.query(
				Query(queue_event.user, defaults.QUERY_AVAILABLE_MOVIES, queue_event.data))
			self.modref.message_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
				'type': defaults.MSG_SOCKET_EDIT_QUERY_AVAILABLE_MOVIES_ANSWER, 'config': movie_list})

	def query_handler(self, queue_event, max_result_count):
		''' try to send simulated answers
		'''
		print("simulator query handler", queue_event.type,
			  queue_event.user, max_result_count)
		if queue_event.type == defaults.QUERY_FEASIBLE_DEVICES:
			return ['TV Wohnzimmer-S', 'TV Küche-s', 'Chromecast Büro']
		return[]

	def update_movie_list(self, queue_event):
		'''
		'''
				
		# is it a quick search? Then update the quicksearch data first
		quick_search_name=queue_event.data['query']['name']
		if quick_search_name:
			quick_search_entry=None
			for movie_list_entry in self.movielist.values():
				if movie_list_entry['query'] and movie_list_entry['query']['name'].lower()==quick_search_name.lower() and queue_event.user.name in movie_list_entry['clients']:
					quick_search_entry=movie_list_entry
					break
			if not quick_search_entry:
				quick_search_entry = {
					'clients': {},
				}
				quick_search_entry['clients'][queue_event.user.name] = {}
				# new entry, so it gets its own identifier
				quick_search_entry_id = str(uuid.uuid4())
				self.movielist[quick_search_entry_id] = quick_search_entry
			quick_search_entry['type'] = defaults.MOVIE_TYPE_TEMPLATE
			quick_search_entry['query'] = queue_event.data['query']
			quick_search_entry['movie_info']= MovieInfo(
				'0',  # id
				quick_search_name,  # title
				'',  # type
				'',  # source
				'',  # date
				'',  # duration
				'',  # viewed
				''  # description
			)


		movie_list = self.modref.message_handler.query(
			Query(queue_event.user, defaults.QUERY_MOVIE_ID, queue_event.data['movie_info_id']))
		if movie_list:
			# TODO
			# ist es ein Live- Movie? Dann wird es als Live- Schnipsl angehängt
			# ist es ein benamter Quick-Search? Gibt es ihn schon oder ist er neu?
			# ist ein normaler Stream?
			# ist es ein Record- Eintrag?
			movie_list_id = queue_event.data['edit_id']
			if movie_list_id in self.movielist and not quick_search_name:  # an existing entry was edited, and it was not a quicksearch
				print("Molist Eintrag existiert schon")
				movie_list_entry = self.movielist[movie_list_id]
			else:
				movie_list_entry = {

					'clients': {},

				}
				movie_list_entry['clients'][queue_event.user.name] = {}
				# new entry, so it gets its own identifier
				movie_list_id = str(uuid.uuid4())
				self.movielist[movie_list_id] = movie_list_entry
			movie_list_entry['type'] = movie_list[0].source_type
			movie_list_entry['query'] = queue_event.data['query']
			#as this is not a quicksearch entry anymore, we must make sure that it does not contain a 
			# quicksearch name anymore
			movie_list_entry['query']['name']=''
			movie_list_entry['movie_info']= MovieInfo(
				queue_event.data['movie_info_id'],  # id
				movie_list[0].title,  # title
				movie_list[0].category,  # type
				movie_list[0].provider,  # source
				movie_list[0].timestamp,  # date
				movie_list[0].duration,  # duration
				'0%',  # viewed
				movie_list[0].description  # description
			)

			return movie_list_id, movie_list[0].uri()
		else:
			return None

	def filter_select_values(self, value_list, actual_values):
		'''returns list of the values of actual_values, which are included in value list
		'''
		res = []
		for value in actual_values:
			if value in value_list:
				res.append(value)
		return res

	def update_single_movie_clip(self, id):
		self.modref.message_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
			'type': defaults.MSG_SOCKET_HOME_MOVIE_INFO_UPDATE, 'config': {'id': id, 'movie_info': self.movielist[id]}})

	def send_player_status(self):
		self.player_info['position'] = self.play_time * \
			100 // self.play_total_secs
		self.player_info['playTime'] = '{:02d}:{:02d}'.format(
			self.play_time//60, self.play_time % 60)
		self.player_info['remainingTime'] = '{:02d}:{:02d}'.format(
			(self.play_total_secs-self.play_time)//60, (self.play_total_secs-self.play_time) % 60)
		self.modref.message_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
			'type': 'app_player_pos', 'config': self.player_info})

	def send_home_movie_list(self, original_queue_event):
		new_event = copy.copy(original_queue_event)
		new_event.type = defaults.MSG_SOCKET_MSG
		new_event.data = {
			'type': defaults.MSG_SOCKET_HOME_MOVIE_INFO_LIST, 'config': self.prepare_movie_list(original_queue_event.user)}
		#print("new_event", new_event.data['config'])
		self.modref.message_handler.queue_event_obj(new_event)


	def send_player_devices(self, devices,movie_id):
		# we set the device info
		data = {
			'actual_device': '',
			'devices': devices,
			'movie_id':movie_id
		}
		self.modref.message_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
			'type': defaults.MSG_SOCKET_QUERY_FEASIBLE_DEVICES_ANSWER, 'config': data})

	def play_request(self, queue_event):
		# starts to play movie on device
		print("plays schnipsl {0} on device ".format(queue_event.data['movie_id']))

	def send_movie_info(self, movie_list_id):
		self.modref.message_handler.queue_event(None, defaults.MSG_SOCKET_MSG, {
			'type': defaults.MSG_SOCKET_APP_MOVIE_INFO, 'config': self.movielist[movie_list_id]['movie_info']})

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
