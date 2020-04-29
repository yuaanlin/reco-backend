from db import repeats_collection
from db import calendars_collection

from classes.Event import Event

from utils.date import Range, range_overlap
from datetime import datetime, timedelta

from functions.update_repeat import update_repeat
from functions.update_event import update_event

import calendar
import numpy
import uuid


def build_repeat(userid, year, month):
    '''Build all events which create by repeat in certain month

    Args:
        userid (str): ID of the user.
        year (int): The year you want to build events.
        month (int): The month you want to build events.
    '''

    target_range_start = datetime(year, month, 1, 0, 0, 0)
    target_range_end = datetime(
        year, month, calendar.monthrange(year, month)[1], 23, 59, 59)

    target_range = Range(target_range_start, target_range_end)

    for cal in calendars_collection.find({'owner': userid}):
        calendar_id = cal['_id']
        for repeat in repeats_collection.find({'calendar': calendar_id}):
            repeat_range = Range(repeat['startDate'], repeat['endDate'])

            # If this repeat is in target range.
            if range_overlap(target_range, repeat_range) > 0:

                new_generated = repeat['generated']

                # Iterate all days in target range.
                pointer = target_range_start
                while pointer <= target_range_end:

                    # Check if this day should have a evnet accroding to repeat but it hasnt.
                    pointer_day_string = pointer.strftime("%Y/%-m/%-d")
                    if (repeat['cycle'] == 'Week' and int(repeat['repeatData']) - 1 == pointer.weekday(
                    ) and pointer_day_string not in repeat['generated']) or (
                            repeat['cycle'] == 'Month' and int(repeat['repeatData']) == pointer.day and pointer_day_string not in repeat['generated']):

                        # Add this day into new generated array
                        new_generated.append(pointer_day_string)

                        # Compose new Event
                        new_event = Event()
                        new_event._id = str(uuid.uuid4())
                        new_event.title = repeat['title']
                        new_event.calendar = cal['_id']
                        new_event.color = cal['color']
                        new_event.startTime = pointer.replace(
                            hour=repeat['startTime'].hour, minute=repeat['startTime'].minute, second=repeat['startTime'].second)
                        new_event.endTime = pointer.replace(
                            hour=repeat['endTime'].hour, minute=repeat['endTime'].minute, second=repeat['endTime'].second)

                        # Upload new event database
                        update_event(new_event)

                    pointer += timedelta(days=1)

                # Update the generated array
                repeat['generated'] = new_generated
                update_repeat(repeat)
