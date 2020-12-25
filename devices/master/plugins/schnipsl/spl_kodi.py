#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard module
import json
import os
import sys
import time
from base64 import b64encode
from pprint import pprint

from threading import Timer , Lock


import requests
import zeroconf



# Non standard modules (install with pip)


# own local modules
ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))

import defaults
from classes import MovieInfo
from messagehandler import Query
from splthread import SplThread

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
		self.current_time=-1
		self.duration=0
		self.player_id=0
		self.cast_info  = {
				'device_friendly_name': self.device_friendly_name,
				'duration': 0,
				'current_time': 0,
				'play':  False,
				'volume': 0,
				'state_change': True
			}

# usefull link: https://www.loxwiki.eu/plugins/servlet/mobile?contentId=60556203#content/view/60556203


	def play_media(self,movie_url,movie_mime_type,current_time=0):

		if not self.cast_info['duration']:
			self.cast_info['duration'] = -1
		if self.supports_seek:
			self.cast_info['current_time'] = 0
		else:
			self.cast_info['current_time'] = -1

		print('Kodi play request',movie_url)
		payload ={
			"jsonrpc":"2.0",
			"id":1,
			"method": "Player.Open",
			"params":{
				"item":{
					"file":movie_url
				}
			}
		}
		response=self.doJsonRPC(payload)
		print("wo ist die richtige PlayerID??")
		try:
			self.cast_info['play']=response['result']=='OK'
		except:
			self.cast_info['play']=False
		self.player_id=1
		self.update_status()
		if self.cast_info['play'] and self.supports_seek and current_time>0:
			self.seek(current_time)

	def play(self):
		print('Kodi play')
		payload ={
			"jsonrpc":"2.0",
			"id":1,
			"method": "Player.PlayPause",
			"params":{
				"playerid": self.player_id,
				"play": True
			 }
		}
		self.doJsonRPC(payload)

	def seek(self, position):
		print('Kodi seek')
		try:
			duration=position *100/self.duration
		except: #catch devision py zero
			duration=0
		payload ={
			"jsonrpc":"2.0",
			"id":1,
			"method": "Player.Seek",
			"params":{
				"playerid": self.player_id,
				"value": duration
			 }
		}
		self.doJsonRPC(payload)

	def pause(self):
		print('Kodi pause')
		payload ={
			"jsonrpc":"2.0",
			"id":1,
			"method": "Player.PlayPause",
			"params":{
				"playerid": self.player_id,
				"play": False
			 }
		}
		self.doJsonRPC(payload)

	def stop(self):
		print('Kodi stop')
		payload ={
			"jsonrpc":"2.0",
			"id":1,
			"method": "Player.Stop",
			"params":{
				"playerid": self.player_id
			 }
		}
		self.doJsonRPC(payload)

	def update_status(self):
		payload ={
			"jsonrpc":"2.0",
			"id":1,
			"method": "Player.GetProperties",
			"params":{
				"properties": [
					"type",
					"totaltime",
					"canseek",
					"live",
					"speed",
					"position",
					"time",
					"playlistid"
				],
				"playerid": self.player_id
			}
		}
		response=self.doJsonRPC(payload)
		try:
			self.cast_info['duration']=self.time_to_timestamp(response['result']['totaltime'])
			self.cast_info['current_time']=self.time_to_timestamp(response['result']['time'])
			self.supports_seek=response['result']['canseek']
			self.supports_pause=not response['result']['live']
			self.duration=self.cast_info['duration']
			self.current_time=self.cast_info['current_time']
			previous_player_state=self.cast_info['play']
			self.cast_info['play']=response['result']['speed']>0
			self.cast_info['state_change']=previous_player_state and not self.cast_info['play']
		except:
			self.cast_info['state_change']=False

		payload ={
			"jsonrpc":"2.0",
			"id":1,
			"method": "Application.GetProperties",
			"params":{
				"properties": [
					"volume"
				],
				#"playerid": self.player_id
			}
		}
		response=self.doJsonRPC(payload)
		try:
			self.cast_info['volume']=response['result']['volume']
			pass
		except:
			pass

	def set_volume(self, volume):
		print('Kodi set_volume',volume)
		payload ={
			"jsonrpc":"2.0",
			"id":1,
			"method": "Application.SetVolume",
			"params":{ "volume": volume }
		}
		self.doJsonRPC(payload)

	def doJsonRPC(self,payload):
		try:
			url='http://'+self.host+':8080/jsonrpc'
			response = requests.post(url, json=payload).json()
			#print(payload,response)
			return response
		except:
			return None

	def time_to_timestamp(self,time_struct):
		try:
			return time_struct['hours']*3600+time_struct['minutes']*60+time_struct['seconds']
		except:
			return 0



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
		self.lock=Lock()

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
			cast = self.get_cast(queue_event.data['device_friendly_name'])
			if cast and cast.online:
				print(repr(cast))
				cast.stop()

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
			# schnipsl handles the volume as percent value from 1 to 100, Kodi also from 0 .. 100
			volume = int(queue_event.data['volume'])
			if cast:
				self.set_volume(cast, volume)

		# for further pocessing, do not forget to return the queue event
		return queue_event

	def query_handler(self, queue_event, max_result_count):
		''' try to send simulated answers
		'''
		# print("kodi query handler", queue_event.type, queue_event.user, max_result_count)
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
			with self.lock:
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

	def update_service(self, zeroconf, type, uuid):
		# can be empty, but it's required by zeroconfig browser
		pass

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
		if volume > 100:
			volume = 100
		if volume < 0:
			volume = 0
		cast.set_volume(int(volume))

	def send_device_play_status(self, device_friendly_name, state_change_flag):
		if device_friendly_name in self.devices:
			cast = self.devices[device_friendly_name]
			if not cast.online:
				return  # device is actual not acessable
			cast.update_status()

			cast_info =cast.cast_info
			cast_info['state_change']= cast_info['state_change'] or state_change_flag # state change is set either on request or of kodi itself is asking for

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
		self.browser = zeroconf.ServiceBrowser(
			self.zeroconf, "_xbmc-jsonrpc._tcp.local.", self)
		while self.runFlag:
			time.sleep(2)
			with self.lock:
				for device_friendly_name in self.devices:
					self.send_device_play_status(device_friendly_name, False)

	def _stop(self):
		self.zeroconf.close()
		self.runFlag = False



