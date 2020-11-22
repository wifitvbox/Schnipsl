#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import schnipsllogger

logger = schnipsllogger.getLogger(__name__)

class JsonStorage:
	'''loads and saves persistent data as json to disk

	'''

	def __init__(self, filename, default):
		'''
		creates a persistent data link to a config file on disk

		Args:
			filename (:str:`str`): Absolut! path to config file
			default (:obj:`obj`) : serialisable data structure to be used if file does not exist yet

		'''
		self.config = default # just the default
		self.file_name = filename

		try:
			with open(self.file_name) as json_file:
				self.config = json.load(json_file)

		except:
			logger.warning(
				"couldn't load config file {0}".format(self.file_name))
			# self default config to have a configable file on disk
			self.save()


	def read(self, key, default=None):
		''' read value from config, identified by key

		Args:
		key (:obj:`str`): lookup index. if key == 'all', it returns the whole config object
		'''

		if key=='all':
			return self.config
		if key in self.config:
			return self.config[key]
		return default

	def write(self, key, value, delay_write=False):
		''' write value into config, identified by key.
		Saves also straight to disk, if delay_write is not True

		Args:
		key (:obj:`str`): lookup index
		value (:obj:`obj`): value to store
		delay_write (:obj:`boolean`): Do not save now
		'''

		self.config[key] = value
		if not delay_write:
			self.save()

	def save(self):
		''' write config to disk
		'''

		try:
			with open(self.file_name, 'w') as outfile:
				json.dump(self.config, outfile, sort_keys=True,
						  indent=4, separators=(',', ': '))
		except Exception as ex:
			logger.warning("couldn't write config file {0}: {1}".format(
				self.file_name,str(ex)))

