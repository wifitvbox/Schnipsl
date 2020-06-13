#!/usr/bin/env python
# -*- coding: utf-8 -*-

CONFIG_FILE = 'config/config.json'
USER_DATA_FILE = 'config/users.json'
WEB_ROOT_DIR = '../../webapp/dist'

# all the different message types
MSG_SOCKET_CONNECT = 'wsconnect'
MSG_SOCKET_CLOSE = 'wsclose'
MSG_SOCKET_MSG = 'wsmsg'

# all the different query types
QUERY_FEASIBLE_DEVICES = 'feasibledevices'
QUERY_AVAILABLE_SOURCES = 'availablesources'
# limits the number of search results when do a query
MAX_QUERY_SIZE = 40

