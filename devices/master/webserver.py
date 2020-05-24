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


modules = {}
ws_clients = []


class WSZuulHandler(HTTPWebSocketsHandler):

	def get_module(self, prefix):
		'''returns registered module by name
		'''

		global modules
		try:
			return modules[prefix]
		except:
			return None

	def emit(self, type, config):
		''' sends data object as JSON string to websocket client

		Args:
		type (:obj:`str`): string identifier of the contained data type
		config (:obj:`obj`): data object to be sent
		'''

		message = {'type': type, 'config': config}
		self.send_message(json.dumps(message))

	def on_ws_message(self, message):
		''' distributes incoming messages to the registered modules

		the receiver is identified by the prefix of the message 'type'

		the modules register their prefix during the 'register' function

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

		else:
			unknown_msg = True
			global modules
			for id, module in modules.items():
				if data['type'].lower().startswith(id):
					module["msg"](data, self.user)
					unknown_msg = False
			if unknown_msg:
				self.log_message("Command not found:"+data['type'])

	def on_ws_connected(self):
		''' informs all registered modules on websocket connect about that new connection
		'''
		#self.log_message('%s', 'websocket connected')
		self.user = WebsocketUser("", self)
		global ws_clients
		ws_clients.append(self.user)
		global modules
		for module in modules.values():
			module["onWebSocketOpen"](self.user)

	def on_ws_closed(self):
		''' informs all registered modules on websocket close about the closed connection
		'''

		#self.log_message('%s', 'websocket closed')
		global ws_clients
		ws_clients.remove(self.user)
		global modules
		for module_name, module in modules.items():
			module["onWebSocketClose"](self.user)

	def setup(self):
		'''initialise the websocket
		'''

		super(HTTPWebSocketsHandler, self).setup()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	'''Threaded HTTP and Websocket server'''

	def register(self, prefix, module, wsMsghandler, wsOnOpen, wsOnClose):
		''' register other modules as Websocket message consumers

		Args:
		prefix (:obj:`string`): hash containing all active users as copy
		module (:obj:`obj`): hash containing all active users as copy
		wsMsghandler (:obj:`function`): the callback function when receiving a message
		wsOnOpen (:obj:`function`): the callback function when a websocket connects
		wsOnClose (:obj:`function`):: the callback function when a websocket closes
		'''

		global modules
		modules[prefix] = {'module': module, 'msg': wsMsghandler,
						   'onWebSocketOpen': wsOnOpen, 'onWebSocketClose': wsOnClose}

	def get_module(self, prefix):
		'''returns registered module by name
		'''

		global modules
		try:
			return modules[prefix]
		except:
			return None

	def emit(self, topic, data):
		'''broadcasts a message to all connected websocket clients
		'''
		global ws_clients
		for user in ws_clients:
			user.ws.emit(topic, data)


class Webserver(SplThread):

	def __init__(self, modref):
		''' creates the HTTP and websocket server
		'''

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

