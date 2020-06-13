#!/usr/bin/env python
# -*- coding: utf-8 -*-


class MovieInfo(dict):
	'''helper class to store the movie clips information to sent to the client
	'''

	def __init__(self, title, category, source, date, duration, viewed, description):
		self['title'] = title
		self['category'] = category
		self['source'] = source
		self['date'] = date
		self['duration'] = duration
		self['viewed'] = viewed
		self['description'] = description

class Source:
	'''object holds all information about a movie clip source
	'''
	def __init__(
		self,
		source='',
		provider='',
		channel='',
		title='',
		timestamp='',
		duration='',
		description='',
		url=''
		):
		self.source=source
		self.provider=provider
		self.channel=channel
		self.title=title
		self.timestamp=timestamp
		self.duration=duration
		self.description=description
		self.url=url
		self.streams={}

	def add_stream(self, type ,resolution, url):
		'''stores the different media streams of a source
		'''

		if not type in self.streams:
			self.streams[type]={}
		self.streams[type][resolution]=url
	
	def uri(self):
		'''returns a descriptor which shall be good enough to identify a source inside a source database, 
		even if the uri comes from another snipsl instance

		TODO: make the uri shorter
		'''
		return ':'.join([self.source,self.provider,self.timestamp])