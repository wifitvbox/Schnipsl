#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

import schnipsllogger
import translate
import user
import defaults

_ = translate.gettext

logger = schnipsllogger.getLogger(__name__)


class Storage:
	'''loads and saves all persistent data to disk

	Provides also some helper functions for some data elements


The users.json contains the living data of the system, while config.json contains the more static data.
The config.json can be manipulated through the web interface

Format of users.json:
.. code-block:: json

	{
			TODO Explain the Structure
	}


Format of config.json:
.. code-block:: json
	{
			TODO Explain the Structure
	}

	'''

	def __init__(self, modref):
		''' loads all data files'''
		self.config = {}
		self.modref = modref
		self.users = {'movie_list': {}, }  # just empty lists
		self.config_file_name = os.path.join(
			os.path.dirname(__file__), defaults.CONFIG_FILE)
		self.users_file_name = os.path.join(
			os.path.dirname(__file__), defaults.USER_DATA_FILE)

		try:
			with open(self.config_file_name) as json_file:
				self.config = json.load(json_file)

		except:
			logger.warning(
				"couldn't load config file {0}".format(self.config_file_name))
			self.config={

				"server_config": {
					"credentials": "",
					"host": "0.0.0.0",
					"port": 8000,
					"secure": False
				},
			}

		try:
			with open(self.users_file_name) as json_file:
				self.users = json.load(json_file)

		except:
			logger.warning("couldn't load users file {0}".format(
				self.users_file_name))




	def config_keys(self):
		'''provides config values allowed to change by the web interface
		'''
		return ['admins', 'messenger_token', 'timetolive']

	def msg(self, data, ws_user):
		''' handles incoming websocket messages

		Args:
		data (:obj:`obj`): data object
				type (:obj:`str`) : type of data
				config (:obj:`obj`): various data
		ws_user (:obj:`boolean`): websocket client object, needed to reply on messages
		'''

		if data['type'] == 'st_tree':
			config = {}
			ws_user.ws.emit(
				"tree", {'user_data': self.users, 'config_data': config})

	def dummy(self, user):
		''' empty procedure for websocket connect/disconnect handler
		'''
		pass

	def read_config_value(self, key, default=None):
		''' read value from config, identified by key

		Args:
		key (:obj:`str`): lookup index
		'''

		if key in self.config:
			return self.config[key]
		return default

	def write_config_value(self, key, value, delay_write=False):
		''' write value into config, identified by key.
		Saves also straight to disk, if delay_write is not True

		Args:
		key (:obj:`str`): lookup index
		value (:obj:`obj`): value to store
		delay_write (:obj:`boolean`): Do not save now
		'''

		self.config[key] = value
		if not delay_write:
			self.save_config()

	def read_users_value(self, key, default=None):
		''' read value from users, identified by key

		Args:
		key (:obj:`str`): lookup index
		'''

		if key in self.users:
			return self.users[key]
		return default

	def write_users_value(self, key, value, delay_write=False):
		''' write value into users, identified by key.
		Saves also straight to disk, if delay_write is not True

		Args:
		key (:obj:`str`): lookup index
		value (:obj:`obj`): value to store
		delay_write (:obj:`boolean`): Do not save now
		'''

		self.users[key] = value
		if not delay_write:
			self.save_users()

	def save_config(self):
		''' write config to disk
		'''

		try:
			with open(self.config_file_name, 'w') as outfile:
				json.dump(self.config, outfile, sort_keys=True,
						  indent=4, separators=(',', ': '))
		except:
			logger.warning("couldn't write config file {0}".format(
				self.config_file_name))


	def save_users(self):
		''' Saves the users to disk
		'''

		try:
			with open(self.users_file_name, 'w') as outfile:
				json.dump(self.users, outfile, sort_keys=True,
						  indent=4, separators=(',', ': '))
		except Exception as ex:
			logger.warning("couldn't write users file {0} because {1}".format(
				self.users_file_name, ex))

	def get_users(self):
		''' returns the user data reference
		'''
		return self.users
