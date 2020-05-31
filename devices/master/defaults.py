#!/usr/bin/env python
# -*- coding: utf-8 -*-

# how long shall a deleted user/time time be kept for recovery before final deletion?
DELETE_AFTER_DAYS = 30
ENTRY_SLOTS_PER_HOUR = 2  # equals half hour
FORECAST_DAYS = 7  # how many days are in the time table
# no time table editor implemented yet, so we've only one single value for the whole time
#TIME_TABLE_SIZE= ENTRY_SLOTS_PER_HOUR * 24 * FORECAST_DAYS
TIME_TABLE_SIZE = 1
TIME_TO_LIVE = 5  # how often a key can be lend further forward
SMART_HOME_TIMEOUT = 2.0  # secs to wait for an answer from smart home interface
CONFIG_FILE = 'config/config.json'
USER_DATA_FILE = 'config/users.json'
WEB_ROOT_DIR = '../../webapp/dist'


# all the different message types
MSG_SOCKET_CONNECT = 'wsconnect'
MSG_SOCKET_CLOSE = 'wsclose'
MSG_SOCKET_MSG = 'wsmsg'