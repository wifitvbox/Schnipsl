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
import threading
import uuid
from pprint import pprint

# Non standard modules (install with pip)

import pychromecast
import zeroconf

# own local modules
ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))


class SplPlugin(SplThread):
	plugin_id='chromecast'
	plugin_names=['Chromecast']

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

		##### plugin specific stuff
		self.chromecasts = {}


	def event_listener(self, queue_event):
		if queue_event.type == defaults.DEVICE_PLAY_REQUEST:
			cast= self.get_cast(queue_event.data['device_friendly_name'])
			if cast:
				pass # was mache ich da jetzt mit?!?!
			chromecasts, browser= pychromecast.get_listed_chromecasts(friendly_names=[queue_event.data['device_friendly_name']])
			if chromecasts:
				cast=list(chromecasts)[0]
				cast.wait()
				print(cast.device)
				print(cast.status)
				# CastStatus(is_active_input=True, is_stand_by=False, volume_level=1.0, volume_muted=False, app_id='CC1AD845', display_name='Default Media Receiver', namespaces=['urn:x-cast:com.google.cast.player.message', 'urn:x-cast:com.google.cast.media'], session_id='CCA39713-9A4F-34A6-A8BF-5D97BE7ECA5C', transport_id='web-9', status_text='')
				mc = cast.media_controller
				mc.play_media(queue_event.data['movie_url'],queue_event.data['movie_mime_type'])
				mc.block_until_active()
				print(mc.status)
				self.chromecasts[queue_event.data['device_friendly_name']]=cast
				# MediaStatus(current_time=42.458322, content_id='http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4', content_type='video/mp4', duration=596.474195, stream_type='BUFFERED', idle_reason=None, media_session_id=1, playback_rate=1, player_state='PLAYING', supported_media_commands=15, volume_level=1, volume_muted=False)


		if queue_event.type == defaults.DEVICE_PLAY_PAUSE:
			cast= self.get_cast(queue_event.data['device_friendly_name'])
			if cast and cast.media_controller.status.supports_pause:
				cast.media_controller.pause()
				print(cast.media_controller.status)

		if queue_event.type == defaults.DEVICE_PLAY_RESUME:
			cast= self.get_cast(queue_event.data['device_friendly_name'])
			if cast and cast.media_controller.status.supports_pause:
				cast.media_controller.play()
		if queue_event.type == defaults.DEVICE_PLAY_SETPOS:
			cast= self.get_cast(queue_event.data['device_friendly_name'])
			pos=queue_event.data['pos']
			if cast:
				self.set_seek(cast,pos)
		if queue_event.type == defaults.DEVICE_PLAY_SETVOLUME:
			cast= self.get_cast(queue_event.data['device_friendly_name'])
			volume=queue_event.data['volume'] / 100 # schnipsl handles the volume as percent value from 1 to 100, chromecasts from 0 .. 1.0
			if cast:
				self.set_volume(cast,volume)
		if queue_event.type == defaults.DEVICE_PLAY_STOP:
			pass


		# for further pocessing, do not forget to return the queue event
		return queue_event

	def query_handler(self, queue_event, max_result_count):
		''' try to send simulated answers
		'''
		print("chromecast query handler", queue_event.type,
			  queue_event.user, max_result_count)
		if queue_event.type == defaults.QUERY_FEASIBLE_DEVICES:
			res=[]
			print("start storing chromecast devices")
			for service_tuple in self.listener.services.values():
				service_list=list(service_tuple)
				device_type=service_list[2]
				device_friedly_name=service_list[3]
				res.append(device_friedly_name)
				print("add chromecast device_friedly_name {0}",device_friedly_name)
			print("end storing chromecast devices")
			return res[:max_result_count]
		return[]

	def get_cast(self, device_friendly_name):
		try:
			return self.chromecasts[device_friendly_name]
		except:
			return None


	def list_devices(self):
		print("Currently known cast devices:")
		for uuid, service in self.listener.services.items():
			print("  {} {}".format(uuid, service))

	def add_callback(self, uuid, name):
		print("Found mDNS service for cast device_friedly_name {}".format(uuid))
		self.list_devices()

	def remove_callback(self, uuid, name, service):
		print("Lost mDNS service for cast device_friedly_name {} {}".format(uuid, service))
		self.list_devices()

	def update_callback(self, uuid, name):
		print("Updated mDNS service for cast device_friedly_name {}".format(uuid))
		self.list_devices()

	def set_seek(self,cast, position):
		if cast.media_controller.status.supports_seek is False:
			return
		cast.media_controller.update_status()
		if position > cast.media_controller.status.duration:
			return
		if position < 0:
			position = 0
		cast.media_controller.seek(position)


	def set_volume(self,cast, volume):
		if volume > 1.0:
			volume = 1.0
		if volume < 0.0:
			volume = 0.0
		cast.set_volume(volume)

	def send_device_play_status(self,device_friendly_name, cast, state_change_flag):
		cast.media_controller.update_status()
		chromecast_info={
			'device_friendly_name': device_friendly_name,
			'duration' : cast.media_controller.status.duration,
			'time' : cast.media_controller.status.current_time,
			'play' : cast.media_controller.status.player_state  == "PLAYING",
			'volume' : cast.status.volume_level,
			'state_change' : state_change_flag
		}
		if cast.media_controller.status.supports_seek:
			chromecast_info['time']=cast.media_controller.status.current_time
		else:
			chromecast_info['time']=-1
		self.modref.message_handler.queue_event(None, defaults.DEVICE_PLAY_STATUS, chromecast_info)


	def _run(self):
		''' starts the server
		'''
		self.listener = pychromecast.CastListener(self.add_callback, self.remove_callback, self.update_callback)
		zconf = zeroconf.Zeroconf()
		self.browser = pychromecast.discovery.start_discovery(self.listener, zconf)
		tick = 0
		while self.runFlag:
			time.sleep(5)
			for device_friendly_name, cast in self.chromecasts.items():
				self.send_device_play_status(device_friendly_name, cast, False)


	def _stop(self):
		pychromecast.stop_discovery(self.browser)
		self.runFlag = False
