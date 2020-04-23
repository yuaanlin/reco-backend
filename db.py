# -*- coding: utf-8 -*-
from pymongo import MongoClient

import json

# get config
with open('config.json') as f:
    config = json.load(f)

# connect to mongodb cluster
conn = MongoClient(config['MongoDB_Connect_String'])

# database
db = conn.data

# collections
users_collection = db.users
sessions_collection = db.sessions
calendars_collection = db.calendars
events_collection = db.events
todos_collection = db.todos
repeats_collection = db.repeats
