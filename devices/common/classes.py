#!/usr/bin/env python
# -*- coding: utf-8 -*-

import defaults

class MovieInfo(dict):
	'''helper class to store the movie clips information to sent to the client
	'''

	@classmethod
	def movie_to_movie_info(cls,movie,category):
		return MovieInfo(
					movie.uri(),
					movie.title,
					category,
					movie.provider,
					movie.timestamp,
					movie.duration,
					movie.description
				)

	def __init__(self, uri, title, category, provider, timestamp, duration, description,query=None):
		self['uri'] = uri
		self['query'] = query
		self['title'] = title
		self['category'] = category		# for live stream infos this will be used as the title of the 2. movie
		self['provider'] = provider
		self['timestamp'] = timestamp	# for live stream infos this will be used as the start time of the 2. movie
		self['duration'] = duration 	# for live stream infos this will be used as the remaining time of the 1. movie
		self['description'] = description
		self['description_show'] = False # helper flag for Vue
		self['streamable'] = False # e.g. EPG items can not be streamed, only recorded
		self['recordable'] = False # live streams can not be recorded, as they don't have a duration, they are endless


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