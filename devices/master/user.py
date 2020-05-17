#!/usr/bin/env python
# -*- coding: utf-8 -*-


class User(dict):
	'''helper class to store user data
	'''

	def __init__(self, first_name, last_name, id, language):
		self['first_name'] = self.supress_none(first_name)
		self['last_name'] = self.supress_none(last_name)
		self['user_id'] = str(id)
		self['language'] = language

	def supress_none(self, text):
		if text:
			return text
		return ""
