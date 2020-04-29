# -*- coding: utf-8 -*-

from flask import Flask, request
from dateutil import parser
from checksession import checksession
from date import Range, range_overlap
from db import users_collection, sessions_collection, calendars_collection, events_collection, todos_collection, repeats_collection
from datetime import datetime, timedelta

import calendar
import logging
import json
import uuid


app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello, This is backend of Project Reco.'

# Session 登入
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
    else:  # Session 已過期
        return 'Session is not availible', 401

# 下載某個月的資料
@app.route('/getdata', methods=['GET'])
def getEvents():
    try:
        year = int(request.args.get('year'))
        month = int(request.args.get('month'))
    except:
        return 'Please use Reco Client', 403

    sessionID = request.headers['Authorization']
    if checksession(sessionID):
        target_range = Range(datetime(year, month, 1, 0, 0, 0), datetime(
            year, month, calendar.monthrange(year, month)[1], 23, 59, 59))

        # 用戶 id
        userid = sessions_collection.find_one({'_id': sessionID})['user']

        # 用戶的行事曆
        calendars = calendars_collection.find({'owner': userid})
        calendarIDs = []
        for the_calendar in calendars:
            calendarIDs.append(the_calendar['_id'])

        # 打包 Events 和 Todos
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
                    events.append(event)

            for todo in todos_collection.find({'calendar': calendarID}):

                day_range = Range(todo['deadline'], todo['deadline'])
                if range_overlap(target_range, day_range) > 0:

                    todo['deadline'] = todo['deadline'].strftime(
                        '%Y-%m-%dT%H:%M:%S')
                    todos.append(todo)

        return json.dumps({'events': events, 'todos': todos}, ensure_ascii=False)

    else:  # Session 已過期
        return 'Session is not availible', 401


@app.route('/write-event', methods=['POST'])
def write_event():

    data = request.get_json()

    if data == None or 'event' not in data:  # 請求格式不符
        return 'Please use Reco Client', 403

    sessionID = request.headers['Authorization']
    if checksession(sessionID):

        # 新 Event 資料
        new_event = data['event']
        new_event['startTime'] = parser.parse(new_event['startTime'])
        new_event['endTime'] = parser.parse(new_event['endTime'])

        if events_collection.find_one({'_id': new_event['_id']}) != None:
            events_collection.replace_one(
                {'_id': new_event['_id']}, new_event)
            return "This Event has been updated successfully", 200
        else:
            events_collection.insert_one(new_event)
            return "This Event has been inserted successfully", 200
    else:  # Session 已過期
        return 'Session is not availible', 401


@app.route('/write-todo', methods=['POST'])
def write_todo():

    data = request.get_json()

    if data == None or 'todo' not in data:  # 請求格式不符
        return 'Please use Reco Client', 403

    sessionID = request.headers['Authorization']
    if checksession(sessionID):

        # 新 Todo 資料
        new_todo = data['todo']
        new_todo['deadline'] = parser.parse(new_todo['deadline'])

        if todos_collection.find_one({'_id': new_todo['_id']}) != None:
            todos_collection.replace_one(
                {'_id': new_todo['_id']}, new_todo)
            return "This Todo has been updated successfully", 200
        else:
            todos_collection.insert_one(new_todo)
            return "This Todo has been inserted successfully", 200
    else:  # Session 已過期
        return 'Session is not availible', 401


@app.route('/delete-item', methods=['POST'])
def deleteitem():

    data = request.get_json()

    if data == None or '_id' not in data:  # 請求格式不符
        return 'Please use Reco Client', 403

    sessionID = request.headers['Authorization']
    if checksession(sessionID):

        # 用戶 id
        userid = sessions_collection.find_one({'_id': sessionID})['user']

        for calendar in calendars_collection.find({'owner': userid}):

            events = events_collection.find({'calendar': calendar['_id']})
            for event in events:
                if event['_id'] == data['_id']:
                    events_collection.delete_one({'_id': data['_id']})
                    return 'Delete complete', 200

            todos = todos_collection.find({'calendar': calendar['_id']})
            for todo in todos:
                if todo['_id'] == data['_id']:
                    todos_collection.delete_one({'_id': data['_id']})
                    return 'Delete complete', 200

        return 'Item not found or has been deleted', 404
    else:  # Session 已過期
        return 'Session is not availible', 401


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return '''
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    '''.format(e), 500


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
