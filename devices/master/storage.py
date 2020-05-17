#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json

import zuullogger
import translate
import user
import defaults

_ = translate.gettext

logger = zuullogger.getLogger(__name__)


class Storage:
	'''loads and saves all persistent data to disk

	Provides also some helper functions for some data elements


The users.json contains the living data of the system, while config.json contains the more static data.
The config.json can be manipulated through the web interface

Format of users.json:
.. code-block:: json

	{
			"timetables": { # timetimes contains, which user (A) has lend the key to others (B)
					"1137173018": { # id of user A
							"1": { # unique ID of this this time table, actual always 1, as multiple time tables not implemented yet
									"deletion_timestamp": null, # time stamp, when this table has been deleted to finally remove after some time. Not implemented yed
									"users": {
											"86360813": 1588262644.879617 # time stamp, when this user (user ID B) has been deleted in this time table to finally remove after some time. Not implemented yed
									}
							}
					}
			},
			"users": { #  list of all users, calculated out of the time table
					"86360813": { # user ID
							"time_table": null, # if time table is null, the user does not have access in the moment
							"user": {
									"first_name": "Madlen",
									"language": "de",
									"last_name": "",
									"user_id": "86360813"
							}
					}
			}
	}


Format of config.json:
.. code-block:: json
	{
			"admins": [ # list of user_ids of the users which are admins
					"1137173018"
			],
			"messenger_token": "the Bot API Token", 
			"messenger_type": "telegram",
			"server_config": { # address and port the http/websocket server binds to
					"credentials": "",
					"host": "0.0.0.0",
					"port": 8000,
					"secure": false
			},
			"timetolive": 5, # depth, how often the keys can be lend further forward
			"wallet": { # the collection of own and imported certificates
					"c4ab98b84c": { # the own certificate, the only one containing private key
							"id": "c4ab98b84c",
							"name": "koehlersDoorBot",
							"private": "private key",
							"public": "MEkwEwYHKoZIzj0CAQYIKoZIzj0DAQEDMgAEOUaZAh6IZW9LRqTF0jwMlvw9lNzEZGoKfLlpT/9gkh+Yg0pEi9EuUbYfER9lZot9",
							"timeout": 60 # how old in seconds a power of attorney is allowed to be
					},
					"c8d639c120": { an external certificate, without public key
							"id": "c8d639c120",
							"name": "Meier",
							"public": "MEkwEwYHKoZIzj0CAQYIKoZIzj0DAQEDMgAEIfyEyE605Awm8AFHJXscSVNnFXp34biwMG6SyogdTaKao8aE3XmlWVv6PhSvjsXp"
					}
			}
	}

	'''

	def __init__(self, modref):
		''' loads all data files'''
		self.config = {}
		self.modref = modref
		self.users = {'users': {}, 'timetables': {}}  # just empty lists
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
				"admins": [
				],
				"messenger_token": "",
				"messenger_type": "telegram",
				"server_config": {
					"credentials": "",
					"host": "0.0.0.0",
					"port": 8000,
					"secure": False
				},
				"timetolive": 5,
				"wallet": {
				}
			}

		try:
			with open(self.users_file_name) as json_file:
				self.users = json.load(json_file)

		except:
			logger.warning("couldn't load users file {0}".format(
				self.users_file_name))
		self.create_new_admins_if_any()

	def create_new_admins_if_any(self):
		# copy admin acounts into the user list, if not already in
		for admin in self.get_admin_ids():
			if not admin in self.users['users']:
				self.users['users'][admin] = {'user': user.User(
					'Alice', 'Admin', admin, 'en'), 'time_table': self.create_full_time_table()}

	def create_full_time_table(self):
		''' helper routine to create a full packet time table for the admins

		Return:
		time_table dict
		'''

		res = []
		ttl = self.read_config_value(
			'timetolive', defaults.TIME_TO_LIVE)
		for i in range(defaults.TIME_TABLE_SIZE):  # for each entry slot
			res.append(ttl)
		return res



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
			for key in self.config_keys():
				config[key] = self.config[key]
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

	def get_admin_ids(self):
		''' get list of the admin IDs
		'''
		return self.read_config_value('admins')

	def write_users(self):
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
