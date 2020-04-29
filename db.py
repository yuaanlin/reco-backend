# -*- coding: utf-8 -*-
from pymongo import MongoClient

from utils.bcolors import bcolors

import json
import sys

# get config
with open('apiKey.json') as f:
    config = json.load(f)

# Connect to database
try:
    conn = MongoClient(config['MongoDB_Connect_String'])
    conn.server_info()
except Exception as e:
    print(bcolors.FAIL + 'Connecting to database failed:' + bcolors.ENDC)
    print("Error message: {}".format(e))
    exit()

# database
db = conn.data

# collections
users_collection = db.users
sessions_collection = db.sessions
calendars_collection = db.calendars
events_collection = db.events
todos_collection = db.todos
repeats_collection = db.repeats
