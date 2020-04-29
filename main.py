from flask import Flask, request

from db import users_collection
from db import sessions_collection
from db import calendars_collection
from db import repeats_collection
from db import events_collection
from db import todos_collection

from classes.Event import Event

from utils.checksession import checksession
from utils.date import Range, range_overlap
from utils.bcolors import bcolors

from functions.update_event import update_event
from functions.update_todo import update_todo
from functions.delete_item import delete_item
from functions.build_repeat import build_repeat

from dateutil import parser
from datetime import datetime

import calendar
import logging
import json
import sys
import os


app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, This is backend of Project Reco.'

# Session Login
@app.route('/checksession', methods=['POST'])
def check():
    sessionID = request.headers['Authorization']
    if checksession(sessionID):
        check_result = sessions_collection.find_one({'_id': sessionID})
        userid = check_result['user']
        user = users_collection.find_one({'_id': userid})
        calendars = []
        for calendar in calendars_collection.find({'owner': userid}):
            calendars.append(calendar)
        return json.dumps({"user": user, "calendars": calendars})
    else:  # Session is not availible
        return 'Session is not availible', 401

# Get data of certain month
@app.route('/getdata', methods=['GET'])
def getEvents():
    try:
        year = int(request.args.get('year'))
        month = int(request.args.get('month'))
    except:
        return 'Please use Reco Client', 403

    try:
        sessionID = request.headers['Authorization']
        if checksession(sessionID):

            # Get user id
            userid = sessions_collection.find_one({'_id': sessionID})['user']

            # Build repeats into evnets this month
            build_repeat(userid, year, month)

            # Get calendar IDs
            calendars = calendars_collection.find({'owner': userid})
            calendarIDs = []
            for the_calendar in calendars:
                calendarIDs.append(the_calendar['_id'])

            # Compose target range
            target_range = Range(datetime(year, month, 1, 0, 0, 0), datetime(
                year, month, calendar.monthrange(year, month)[1], 23, 59, 59))

            # Get evnets and todos
            events = []
            todos = []
            for calendarID in calendarIDs:
                for event in events_collection.find({'calendar': calendarID}):

                    day_range = Range(event['startTime'], event['endTime'])
                    if range_overlap(target_range, day_range) > 0:

                        event['startTime'] = event['startTime'].strftime(
                            '%Y-%m-%dT%H:%M:%S')
                        event['endTime'] = event['endTime'].strftime(
                            '%Y-%m-%dT%H:%M:%S')
                        event['_id'] = str(event['_id'])

                        events.append(event)

                for todo in todos_collection.find({'calendar': calendarID}):

                    day_range = Range(todo['deadline'], todo['deadline'])
                    if range_overlap(target_range, day_range) > 0:

                        todo['deadline'] = todo['deadline'].strftime(
                            '%Y-%m-%dT%H:%M:%S')
                        todos.append(todo)

            return json.dumps({'events': events, 'todos': todos}, ensure_ascii=False)

        else:  # Session is not availible
            return 'Session is not availible', 401

    except Exception as e:
        print(bcolors.FAIL +
              'Exception occur when handling /getdata request:' + bcolors.ENDC)
        print('Error: {}'.format(e))
        return 'Internal Server Error', 500


@app.route('/write-event', methods=['POST'])
def write_event():

    try:
        data = request.get_json()

        if data == None or 'event' not in data:  # Request data is in wrong format
            return 'Please use Reco Client', 403

        sessionID = request.headers['Authorization']
        if checksession(sessionID):

            # Compose the new event data
            new_event = Event()
            new_event.fromObject(data['event'])

            # Execute update
            if update_event(new_event):
                return 'Execution success', 200
            else:
                return 'Internal Server Error', 500

        else:  # Session is not availible
            return 'Session is not availible', 401

    except Exception as e:
        exc_type, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(bcolors.FAIL +
              'Exception occur when handling /write-event request:' + bcolors.ENDC)
        print('Error: {}'.format(e))
        print(exc_type, fname, exc_tb.tb_lineno)
        return 'Internal Server Error', 500


@app.route('/write-todo', methods=['POST'])
def write_todo():

    data = request.get_json()

    if data == None or 'todo' not in data:  # Request data is in wrong format
        return 'Please use Reco Client', 403

    sessionID = request.headers['Authorization']
    if checksession(sessionID):

        # Compose the new todo data
        new_todo = data['todo']
        new_todo['deadline'] = parser.parse(new_todo['deadline'])

        # Execute update
        if update_todo(new_todo):
            return 'Execution success', 200
        else:
            return 'Internal Server Error', 500

    else:  # Session is not availible
        return 'Session is not availible', 401


@app.route('/delete-item', methods=['POST'])
def deleteitem():

    data = request.get_json()

    if data == None or '_id' not in data:  # Request data is in wrong format
        return 'Please use Reco Client', 403

    sessionID = request.headers['Authorization']
    if checksession(sessionID):
        userid = sessions_collection.find_one({'_id': sessionID})['user']

        # Execute update
        result = delete_item(userid, data['_id'])
        if result == 200:
            return 'Execution success', 200
        elif result == 404:
            return 'Item not found', 404
        else:
            return 'Internal Server Error', 500

    else:  # Session is not availible
        return 'Session is not availible', 401


@app.errorhandler(500)
def server_error(e):
    logging.exception(bcolors.FAIL + 'An error occurred during a request.')
    return 'Internal Server Error', 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
