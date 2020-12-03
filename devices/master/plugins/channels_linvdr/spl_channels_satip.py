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
from threading import  Lock
import uuid
from pprint import pprint
from urllib.parse import urljoin 
import requests
import re

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
		self.serverConfig = self.modref.store.read_users_value('satipserver', [
			{
				'url':'http://www.satip.info/Playlists/ASTRA_19_2E.m3u',
				'channels_per_device':0
			}
		])

	#------ plugin specific routines

	def loadChannels(self):
		for server in self.serverConfig:
			try:
				f = requests.get(server['url'])
				content=f.text
				match = re.search(r'<ol class="items">(.*)</ol>',content,re.DOTALL)
				if match:
					lines=match.group(1).split('\n')
					item_regex=re.compile(r'<li value=".*"><a href="(.*)" vod  tvid=".*">(.*)</a>')
					plugin_name=self.plugin_names[0]
					source_type=defaults.MOVIE_TYPE_STREAM
					with self.lock:
						for line in lines:
							item_match=re.search(item_regex,line)
							if item_match:
								full_url=urljoin(server['url'],item_match.group(1))
								provider=item_match.group(2)
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
								new_movie.add_stream('ts','',item_match.group(1))
								if not plugin_name in self.movies:
									self.movies[plugin_name]={}
								self.movies[plugin_name][new_movie.uri()]=new_movie


			except Exception as e:
				print(str(e))

