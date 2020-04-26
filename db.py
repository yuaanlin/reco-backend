# -*- coding: utf-8 -*-
from pymongo import MongoClient

import json
import sys

# get config
with open('config.json') as f:
    config = json.load(f)

# Compose the real connection string with command line arguments
try:
    connection_string = config['MongoDB_Connect_String']
    connection_string = connection_string.replace("<username>", sys.argv[1])
    connection_string = connection_string.replace("<password>", sys.argv[2])
except Exception as e:
    print("Compose the connection string failed.")
    print("Error message: {}").format(e)
    print("Maybe you forgot inputing the username and password?")
    exit()

# Connect to database
try:
    conn = MongoClient(connection_string)
    conn.server_info()
except Exception as e:
    print("Connect to database failed.")
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
