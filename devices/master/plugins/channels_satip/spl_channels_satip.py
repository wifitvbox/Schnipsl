#!/usr/bin/env python
# -*- coding: utf-8 -*-


# Standard module
from messagehandler import Query
from classes import MovieInfo
import defaults
from splthread import SplThread
import sys
import os
from base64 import b64encode

from pprint import pprint
import requests
import xmltodict
from urllib.parse import urlparse, urlunparse


# Non standard modules (install with pip)

ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))
# own local modules
from classes import MovieInfo
from classes import Movie
from scheduler import Scheduler
from streamchannels import StreamChannel
from jsonstorage import JsonStorage

class SplPlugin(StreamChannel):
	plugin_id = 'channels_satip'
	plugin_names = ['SatIP Live']

	def __init__(self, modref):
		''' creates the simulator
		'''


		super().__init__(modref)
		modref.message_handler.add_event_handler(
			self.plugin_id, 0, self.event_listener)
		modref.message_handler.add_query_handler(
			self.plugin_id, 0, self.query_handler)


		# plugin specific stuff

		self.origin_dir = os.path.dirname(__file__)
		self.config = JsonStorage(os.path.join(
			self.origin_dir, "config.json"), {
				'channel_file': 'Astra_19.2.xspf',
				'scheme': 'http',
				'netloc': '192.168.1.99'
			}
		)

	#------ plugin specific routines

	def loadChannels(self):
		plugin_name=self.plugin_names[0]
		source_type=defaults.MOVIE_TYPE_STREAM
		try:
			with open(os.path.join(	self.origin_dir,self.config.read('channel_file'))) as fd:
				root = xmltodict.parse(fd.read())
				for track in root['playlist']['trackList']['track']:
					provider=track['title']
					#print (track['album'])
					location=track['location']
					url_st=urlparse(location)
					full_url = urlunparse((
							#url_st.scheme,
							self.config.read('scheme'),
							#url_st.netloc,
							self.config.read('netloc'),
							url_st.path,
							url_st.params,
							url_st.query,
							url_st.fragment,
					))
					#print(full_url)



					self.providers.add(provider)
					new_movie = Movie(
						source=plugin_name,
						source_type=source_type,
						provider=provider,
						category='live',
						title=provider+" Live",
						timestamp="0",
						duration=0,
						description='',
						url=full_url
					)
					new_movie.add_stream('ts','',full_url)
					if not plugin_name in self.movies:
						self.movies[plugin_name]={}
					self.movies[plugin_name][new_movie.uri()]=new_movie


		except Exception as e:
			print(str(e))

