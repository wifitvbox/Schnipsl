#!/usr/bin/env python
# -*- coding: utf-8 -*-

from HTTPWebSocketsHandler import HTTPWebSocketsHandler
'''
credits:
combined http(s) and websocket server copied from
	https://github.com/PyOCL/httpwebsockethandler
	The MIT License (MIT)
	Copyright (c) 2015 Seven Watt

'''


import sys
import os
import threading
import ssl
import json
from base64 import b64encode
import argparse
import time

import threading

from pprint import pprint

from socketserver import ThreadingMixIn
from http.server import HTTPServer
from io import StringIO
from splthread import SplThread
import defaults



class WebsocketUser:
	'''handles all user related data
	'''

	def __init__(self, name, ws):
		self.name = name
		self.ws = ws


modref=None
ws_clients = []


class WSZuulHandler(HTTPWebSocketsHandler):

	def emit(self, type, config):
		''' sends data object as JSON string to websocket client

		Args:
		type (:obj:`str`): string identifier of the contained data type
		config (:obj:`obj`): data object to be sent
		'''

		message = {'type': type, 'config': config}
		self.send_message(json.dumps(message))

	def on_ws_message(self, message):
		''' distributes incoming messages to the registered event handlers

		Args:
				message (:obj:`str`): json string, representing object with 'type' as identifier and 'config' containing the data
		'''

		if message is None:
			message = ''
		#self.log_message('websocket received "%s"', str(message))
		try:
			data = json.loads(message)
		except:
			self.log_message('%s', 'Invalid JSON')
			return
		#self.log_message('json msg: %s', message)

		if data['type'] == 'msg':
			self.log_message('msg %s', data['data'])
		if data['type'] == '_join':
			self.user.name= data['config']['name']

		global modref
		modref.message_handler.queue_event(self.user.name,data['type'],data['config'])

	def on_ws_connected(self):
		''' thows a connect event about that new connection
		'''
		#self.log_message('%s', 'websocket connected')
		self.user = WebsocketUser(None, self)
		global ws_clients
		ws_clients.append(self.user)
		global modref
		modref.message_handler.queue_event(self.user.name,defaults.MSG_SOCKET_CONNECT,None)

	def on_ws_closed(self):
		''' thows a close event about the closed connection
		'''

		#self.log_message('%s', 'websocket closed')
		global ws_clients
		ws_clients.remove(self.user)
		global modref
		modref.message_handler.queue_event(self.user,defaults.MSG_SOCKET_CLOSE,None)

	def setup(self):
		'''initialise the websocket
		'''

		super(HTTPWebSocketsHandler, self).setup()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	'''Threaded HTTP and Websocket server'''

	def emit(self, topic, data):
		'''broadcasts a message to all connected websocket clients
		'''
		global ws_clients
		for user in ws_clients:
			user.ws.emit(topic, data)

	def event_listener(self,queue_event):
		''' checks all incoming queue_events if to be send to one or all users
		'''
		#print("webserver event handler",queue_event.type,queue_event.user)
		if queue_event.type==defaults.MSG_SOCKET_MSG:
			for user in ws_clients:
				if queue_event.user == None or queue_event.user==user.name:
					 user.ws.emit(queue_event.data['type'], queue_event.data['config'])
			return None # no futher handling of this event
		return queue_event


class Webserver(SplThread):

	def __init__(self, act_modref):
		''' creates the HTTP and websocket server
		'''
		global modref
		modref=act_modref

		super().__init__(modref.message_handler,self)
		# reads the config, if any
		server_config = modref.store.read_config_value("server_config")
		# set up the argument parser with values from the config
		parser = argparse.ArgumentParser()
		parser.add_argument("--host", default=server_config["host"],
							help="the IP interface to bound the server to")
		parser.add_argument("-p", "--port", default=server_config["port"],
							help="the server port")
		parser.add_argument("-s", "--secure", action="store_true", default=server_config["secure"],
							help="use secure https: and wss:")
		parser.add_argument("-c", "--credentials",  default=server_config["credentials"],
							help="user credentials")
		args = parser.parse_args()
		self.server = ThreadedHTTPServer((args.host, args.port), WSZuulHandler)
		modref.message_handler.add_event_handler('webserver', 0, self.server.event_listener)
		self.server.daemon_threads = True
		self.server.auth = b64encode(args.credentials.encode("ascii"))
		if args.secure:
			self.server.socket = ssl.wrap_socket(
				self.server.socket, certfile='./server.pem', keyfile='./key.pem', server_side=True)
			print('initialized secure https server at port %d' % (args.port))
		else:
			print('initialized http server at port %d' % (args.port))



	def _run(self):
		''' starts the server
		'''

		try:
			origin_dir = os.path.dirname(__file__)
			web_dir = os.path.join(os.path.dirname(__file__), defaults.WEB_ROOT_DIR)
			os.chdir(web_dir)

			self.server.serve_forever()

			os.chdir(origin_dir)
		except KeyboardInterrupt:
			print('^C received, shutting down server')
			self.server.socket.close()

	def _stop(self):
		self.server.socket.close()

	def  event_listener(self, queue_event):
		''' handler for system events
		'''
		pass

	def query_handler(self, queue_event, max_result_count):
		''' handler for system queries
		'''
		pass

if __name__ == '__main__':
	from storage import Storage
	class ModRef:
		store = None
		message_handler= None

	modref=ModRef()
	modref.store=Storage(modref)
	ws=Webserver(modref)
	ws.run()
	while True:
		time.sleep(1)
	ws.stop()

