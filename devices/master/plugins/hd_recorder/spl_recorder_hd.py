#!/usr/bin/env python
# -*- coding: utf-8 -*-

from splthread import SplThread
from messagehandler import Query
from classes import Movie
import defaults
from scheduler import Scheduler
from jsonstorage import JsonStorage
import json
import os
import sys
import time
import threading
import base64
import subprocess

from urllib.parse import urlparse

# Standard module


# Non standard modules (install with pip)


# own local modules
ScriptPath = os.path.realpath(os.path.join(
	os.path.dirname(__file__), "../../../common"))


# Add the directory containing your module to the Python path (wants absolute paths)
sys.path.append(os.path.abspath(ScriptPath))


class record_states:
	WAIT_FOR_RECORDING = 0
	ACTUAL_RECORDING = 1
	RECORDING_FINISHED = 2
	RECORDING_FAILED = 3  # something went wrong, no result


class SplPlugin(SplThread):
	plugin_id = 'record_hd'
	plugin_names = ['HD Recorder']

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
		self.origin_dir = os.path.dirname(__file__)
		self.config = JsonStorage(os.path.join(
			self.origin_dir, "config.json"), {'path': '/var/schnipsl', 'www-root': 'http://schnipsl:9092/'})
		self.records = JsonStorage(os.path.join(
			self.origin_dir, "records.json"), {})
		self.record_threats={} # we need to store the thread pointers seperate from self.records, as we can't store them as json

	def event_listener(self, queue_event):
		if queue_event.type == defaults.TIMER_RECORD_REQUEST:
			self.timer_record_request(queue_event.data)
		# for further pocessing, do not forget to return the queue event
		return queue_event

	def query_handler(self, queue_event, max_result_count):
		''' try to send simulated answers
		'''
		# print("hd_recorder query handler", queue_event.type,  queue_event.user, max_result_count)
		if queue_event.type == defaults.QUERY_MOVIE_ID:
			new_uri=queue_event.params
			for record_movie in self.records.read('all',{}).values(): # 'all': read the whole config
				if record_movie['new_uri']==new_uri:
					return [Movie(
								source=self.plugin_names[0],
								source_type=defaults.MOVIE_TYPE_RECORD,
								provider=self.plugin_names[0],
								category=record_movie['category'],
								title=record_movie['title'],
								timestamp=record_movie['timestamp'],
								duration=record_movie['duration'],
								description=record_movie['description'],
								url=record_movie['new_url']

					)]

		return[]

	def _run(self):
		''' starts the server
		'''
		scheduler = Scheduler(
			[(self.check_for_records, 30), (self.cleanup_records, 60)])
		while self.runFlag:
			scheduler.execute()
			time.sleep(2)

	def _stop(self):
		self.runFlag = False

	def timer_record_request(self, data):
		uri = data['uri']
		uuid = data['uuid']
		movie_info_list = self.modref.message_handler.query(
			Query(None, defaults.QUERY_MOVIE_ID, uri))
		if movie_info_list:
			movie = movie_info_list[0]
			uri = movie.uri()
			# do we have that record request already
			existing_record = self.records.read(uri)
			if not existing_record:
				path = urlparse(movie.url).path
				ext = os.path.splitext(path)[1]
				if ext.lower()=='.ts':
					ext='.mp4'
				uri_base64 = base64_encode(uri)
				file_path = os.path.join(
					self.config.read('path'), uri_base64+ext)
				if movie.source_type == defaults.MOVIE_TYPE_RECORD:
					self.records.write(uri, {
						# in case of a record we set start and duration to 0 to indicate that the recording can start immediadly & has no duration
						'record_starttime': 0,
						'record_duration': 0,
						'provider': movie.provider,
						'category': movie.category,
						'title': movie.title,
						'timestamp': movie.timestamp,
						'duration': movie.duration,
						'description': movie.description,
						'url': movie.url,

						'uri': uri,
						'new_uri': self.plugin_names[0]+':'+uri_base64,
						'new_url': self.config.read('www-root')+uri_base64+ext,
						'uuid': uuid,
						'ext': ext,
						'file_path': file_path,
						'state': record_states.WAIT_FOR_RECORDING
					})
				if movie.source_type == defaults.MOVIE_TYPE_STREAM:
					self.records.write(uri, {
						'record_starttime': int(movie.timestamp),
						'record_duration': movie.duration,
						'category': movie.category,
						'title': movie.title,
						'timestamp': movie.timestamp,
						'duration': movie.duration,
						'description': movie.description,
						'url': movie.url,

						'uri': uri,
						'new_uri': self.plugin_names[0]+':'+uri_base64,
						'new_url': self.config.read('www-root')+uri_base64+ext,
						'uuid': uuid,
						'ext': ext,
						'file_path': file_path,
						'state': record_states.WAIT_FOR_RECORDING
					})
	
	def path_to_url(self, file_path):
		return file_path

	def check_for_records(self):
		act_time = time.time()
		for uri, record in self.records.config.items():
			if record['state'] == record_states.WAIT_FOR_RECORDING:
				if record['record_duration'] == 0:  # this is a record, which can be recorded immediadly
					record['state'] = record_states.ACTUAL_RECORDING
					self.records.write(uri, record)
					self.recording(record)
					continue
				# something went wrong, the record time was in the past
				if record['record_starttime']+record['record_duration'] < act_time:
					record['state'] = record_states.RECORDING_FAILED
					self.records.write(uri, record)
					self.deploy_record_result(record, False)
					continue
				# it's time to start
				if record['record_starttime']-self.config.read('padding_secs', 300) <= act_time and record['record_starttime']+record['record_duration'] > act_time:
					record['state'] = record_states.ACTUAL_RECORDING
					self.records.write(uri, record)
					self.recording(record)
					continue

	def cleanup_records(self):
		for uri, record in self.records.config.items():
			if uri in self.record_threats:
				# recording is finished, so deploy the result
				if not self.record_threats[uri].is_alive():
					del(self.record_threats[uri])  # we destroy the thread
					self.deploy_record_result(record,
						record['state'] == record_states.RECORDING_FINISHED)
		print('removal of unused recordings not implemented yet')

	def deploy_record_result(self, record, sucess):
		self.modref.message_handler.queue_event(None, defaults.TIMER_RECORD_RESULT, {
			'new_uri':record['new_uri'], 'new_url':record['new_url'], 'uuid': record['uuid'], 'sucess': sucess})

	def recording(self, record):
		uri=record['uri']
		print('try to record ', uri)
		threat = threading.Thread(target=record_thread, args=(
			record, self.config.read('padding_secs', 300)))
		self.record_threats[uri] = threat
		threat.start()


def record_thread(record, padding_time):
	ext = record['ext']
	file_path = record['file_path']
	url = record['url']
	act_time = time.time()
	remaining_time = record['record_starttime']+record['record_duration']-act_time
	attr = None
	if ext.lower() == '.mp4':
		attr = ['curl', '-s', url, '-o', file_path]  # process arguments
	if ext.lower() == '.ts':
		attr = ['ffmpeg', '-y', '-i', url, '-vcodec', 'copy', '-acodec', 'copy',
				'-map', '0:v', '-map', '0:a', '-t', str(remaining_time+padding_time), '-f', 'mp4' , file_path]
	if attr:
		print("recorder started", repr(attr))
		try:
			completed_process = subprocess.run(attr)
			if completed_process.returncode:
				print("recorder ended with an error:\n%s" %
					  (completed_process.returncode))
				record['state'] = record_states.RECORDING_FAILED
			else:
				print("recorder ended")
				record['state'] = record_states.RECORDING_FINISHED
		except Exception as ex:
			print("recorder could not be started. Error: %s" % (ex))
	else:
		record['state'] = record_states.RECORDING_FAILED


def base64_encode(string):
	"""
	Removes any `=` used as padding from the encoded string.
	"""
	encoded = base64.urlsafe_b64encode(string.encode())
	return encoded.decode().replace('=', '')

def base64_decode(string):
	"""
	Adds back in the required padding before decoding.
	"""
	padding = 4 - (len(string) % 4)
	string = string + ("=" * padding)
	return base64.urlsafe_b64decode(string).decode()
