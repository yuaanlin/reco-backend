from db import events_collection
from db import todos_collection

from utils.bcolors import bcolors

from db import calendars_collection

import sys
import os


def delete_item(userid, itemid):
    '''Delete a item whose owner is specified from database accroding to item id

    Args:
        userid (str): The user id of item owner.
        itemid (str): The item id which needs to be deleted.

    Returns:
        200: Delete complete.
        404: Item not found.
        500: Exception occurred.
    '''

    try:

        for calendar in calendars_collection.find({'owner': userid}):

            events = events_collection.find({'calendar': calendar['_id']})
            for event in events:
                if event['_id'] == itemid:
                    events_collection.delete_one({'_id': itemid})
                    return 200

            todos = todos_collection.find({'calendar': calendar['_id']})
            for todo in todos:
                if todo['_id'] == itemid:
                    todos_collection.delete_one({'_id': itemid})
                    return 200

        return 404

    except Exception as e:
        exc_type, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(bcolors.FAIL +
              'Exception occur when handling /write-event request:' + bcolors.ENDC)
        print('Error: {}'.format(e))
        print(exc_type, fname, exc_tb.tb_lineno)
        return 500
