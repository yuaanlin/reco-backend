
from datetime import datetime
from dateutil import parser

import uuid


class Event:
    def __init__(self, _id='', calendar='', title='', startTime=datetime.today(), endTime=datetime.today(), description='', location='', repeatID='', color=['#97A9E1', '#D68DD6'], ignore=False, ignoreReason=''):
        self._id = _id
        self.calendar = calendar
        self.title = title
        self.startTime = startTime
        self.endTime = endTime
        self.description = description
        self.location = location
        self.repeatID = repeatID
        self.color = color
        self.ignore = ignore
        self.ignoreReason = ignoreReason

    def toObject(self):
        return {
            '_id': self._id,
            'calendar': self.calendar,
            'title': self.title,
            'startTime': self.startTime,
            'endTime': self.endTime,
            'description': self.description,
            'location': self.location,
            'repeatID': self.repeatID,
            'color': self.color,
            'ignore': self.ignore,
            'ignoreReason': self.ignoreReason
        }

    def fromObject(self, obj):
        self._id = obj['_id']
        self.calendar = obj['calendar']
        self.title = obj['title']
        self.startTime = parser.parse(obj['startTime'])
        self.endTime = parser.parse(obj['endTime'])
        self.description = obj['description']
        self.location = obj['location']
        self.repeatID = obj['repeatID']
        self.color = obj['color']
        self.ignore = obj['ignore']
        self.ignoreReason = obj['ignoreReason']
