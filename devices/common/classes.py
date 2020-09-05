#!/usr/bin/env python
# -*- coding: utf-8 -*-

import defaults

class MovieInfo(dict):
	'''helper class to store the movie clips information to sent to the client
	'''

	@classmethod
	def movie_to_movie_info(cls,movie,movie_type):
		return MovieInfo(
					movie.uri(),
					movie.title,
					movie_type,
					movie.source,
					movie.timestamp,
					movie.duration,
					movie.description
				)

	def __init__(self, id, title, category, source, date, duration, description,query=None):
		self['id'] = id
		self['query'] = query
		self['title'] = title
		self['category'] = category
		self['source'] = source
		self['date'] = date
		self['duration'] = duration
		self['description'] = description
		self['description_show'] = False

class Movie:
	'''object holds all information about a movie clip source
	'''
	def __init__(
		self,
		source='',
		source_type=defaults.MOVIE_TYPE_RECORD,
		provider='',
		category='',
		title='',
		timestamp='',
		duration='',
		description='',
		url=''
		):
		self.source=source
		self.source_type=source_type
		self.provider=provider
		self.category=category
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