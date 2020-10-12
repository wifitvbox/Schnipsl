#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
import sys
import time
from base64 import b64encode
from pprint import pprint

import defaults
import requests
import zeroconf
from classes import MovieInfo
from messagehandler import Query
# Standard module
from splthread import SplThread

# Non standard modules (install with pip)


# own local modules
ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))


class Kodi:

	def __init__(self, service_info):
		self.device_friendly_name = service_info.name.split('.')[0]
		self.uuid = service_info.name
		self.supports_pause = False
		self.supports_seek = False
		self.online = True
		self.host=service_info.server
		self.port=service_info.port
		self.cast=self
		self.cast_info  = {
				'device_friendly_name': self.device_friendly_name,
				'duration': 0,
				'current_time': 0,
				'play':  False,
				'volume': 0,
				'state_change': True
			}


	def play_media(self,movie_url,movie_mime_type,current_time=0):

		if not self.cast_info['duration']:
			self.cast_info['duration'] = -1
		if self.supports_seek:
			self.cast_info['current_time'] = 0
		else:
			self.cast_info['current_time'] = -1

		url='http://'+self.host+':8080/jsonrpc'
		print('Kodi play request',url)
		payload ={"jsonrpc":"2.0", "id":1, "method": "Player.Open", "params":{"item":{"file":movie_url}}}

		response = requests.post(url, json=payload).json()

		print(response)


	def play(self):
		pass

	def seek(self, position):
		pass

	def pause(self):
		pass

	def update_status(self):
		pass

	def set_volume(self, volume):
		pass


class SplPlugin(SplThread):
	plugin_id = 'kodi'
	plugin_names = ['Kodi']

	def __init__(self, modref):
		''' creates the plugin
		'''
		self.modref = modref

		super().__init__(modref.message_handler, self)
		modref.message_handler.add_event_handler(
			self.plugin_id, 0, self.event_listener)
		modref.message_handler.add_query_handler(
			self.plugin_id, 0, self.query_handler)
		self.runFlag = True

		# plugin specific stuff
		self.devices = {}
		self.zeroconf = zeroconf.Zeroconf()

	def event_listener(self, queue_event):
		if queue_event.type == defaults.DEVICE_PLAY_REQUEST:
			cast = self.get_cast(queue_event.data['device_friendly_name'])
			if cast and cast.online:
				print(repr(cast))
				cast.play_media(
					queue_event.data['movie_url'], queue_event.data['movie_mime_type'], current_time=queue_event.data['current_time'])

		if queue_event.type == defaults.DEVICE_PLAY_PAUSE:
			cast = self.get_cast(queue_event.data['device_friendly_name'])
			if cast and cast.supports_pause:
				cast.pause()
				print(repr(cast))
				self.send_device_play_status(
					queue_event.data['device_friendly_name'], True)

		if queue_event.type == defaults.DEVICE_PLAY_STOP:
			pass

		if queue_event.type == defaults.DEVICE_PLAY_RESUME:
			cast = self.get_cast(queue_event.data['device_friendly_name'])
			if cast and cast.supports_pause:
				cast.play()
		if queue_event.type == defaults.DEVICE_PLAY_SETPOS:
			cast = self.get_cast(queue_event.data['device_friendly_name'])
			pos = queue_event.data['pos']
			if cast and pos:
				self.set_seek(cast, pos)
		if queue_event.type == defaults.DEVICE_PLAY_SETVOLUME:
			cast = self.get_cast(queue_event.data['device_friendly_name'])
			# schnipsl handles the volume as percent value from 1 to 100, chromecasts from 0 .. 1.0
			volume = queue_event.data['volume'] / 100
			if cast:
				self.set_volume(cast, volume)

		# for further pocessing, do not forget to return the queue event
		return queue_event

	def query_handler(self, queue_event, max_result_count):
		''' try to send simulated answers
		'''
		print("kodi query handler", queue_event.type,
			  queue_event.user, max_result_count)
		if queue_event.type == defaults.QUERY_FEASIBLE_DEVICES:
			res = []
			for device_friedly_name in self.devices:
				res.append(device_friedly_name)
			return res[:max_result_count]
		return[]

	def get_cast(self, device_friendly_name):
		try:
			return self.devices[device_friendly_name].cast
		except:
			return None

	def list_devices(self):
		print("Currently known cast devices:")
		for device_friedly_name in self.devices:
			print("  {}".format(device_friedly_name))

	def get_device_friendly_name_of_uuid(self, uuid):
		# kodi specific
		return uuid.split('.')[0]
		'''
		if the uuid is not part of the uuid itself
		for device_friedly_name, cast in self.devices.items():
			if uuid == cast.uuid:
				return device_friedly_name
		return None
		'''

	def add_service(self, zeroconf, type, uuid):
		service_info = zeroconf.get_service_info(type, uuid)
		print("Service %s added, service info: %s" % (uuid, service_info))
		# print("Found mDNS service for cast name {}".format(name))
		device_friendly_name = self.get_device_friendly_name_of_uuid(uuid)
		if device_friendly_name and device_friendly_name in self.devices:
			cast = self.devices[device_friendly_name]
		else:
			cast = Kodi(service_info)
			self.devices[cast.device_friendly_name] = cast
		cast.online = True
		self.list_devices()

	def remove_service(self, zeroconf, type, uuid):
		print("Service %s removed" % (uuid,))
		# print("Lost mDNS service for cast name {} {}".format(
		#	name, service))
		device_friendly_name = self.get_device_friendly_name_of_uuid(uuid)
		if device_friendly_name and device_friendly_name in self.devices:
			cast = self.devices[device_friendly_name]
			cast.online = False
			# sent last known position for later restart
			cast_status = cast.cast_info
			cast_status['state_change'] = True  # set the update marker
			self.modref.message_handler.queue_event(
				None, defaults.DEVICE_PLAY_STATUS, cast_status)
		self.list_devices()

	def set_seek(self, cast, position):
		if cast.supports_seek is False:
			return
		cast.update_status()
		try:
			if position > cast.duration:
				return
			if position < 0:
				position = 0
			cast.seek(position)
		except:
			return

	def set_volume(self, cast, volume):
		if volume > 1.0:
			volume = 1.0
		if volume < 0.0:
			volume = 0.0
		cast.set_volume(volume)

	def send_device_play_status(self, device_friendly_name, state_change_flag):
		if device_friendly_name in self.devices:
			cast = self.devices[device_friendly_name]
			if not cast.online:
				return  # device is actual not acessable
			cast.update_status()

			cast_info =cast.cast_info
			cast_info['state_change']= state_change_flag

			if not cast_info['duration']:
				cast_info['duration'] = -1
			if cast.supports_seek:
				cast_info['current_time'] = cast.current_time
			else:
				cast_info['current_time'] = -1
			cast.cast_info = cast_info
			self.modref.message_handler.queue_event(
				None, defaults.DEVICE_PLAY_STATUS, cast)

	def _run(self):
		''' starts the server
		'''

		listener = MyListener()

		self.browser = zeroconf.ServiceBrowser(
			self.zeroconf, "_xbmc-jsonrpc._tcp.local.", self)
#		self.browser = zeroconf.ServiceBrowser(
#			self.zeroconf, "_xbmc-jsonrpc._tcp.local.", listener)
		while self.runFlag:
			time.sleep(2)
			for device_friendly_name in self.devices:
				self.send_device_play_status(device_friendly_name, False)

	def _stop(self):
		self.zeroconf.close()
		self.runFlag = False

class MyListener:

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))

