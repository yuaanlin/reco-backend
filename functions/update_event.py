from db import events_collection

from utils.bcolors import bcolors


def update_event(event):
    '''Create a new Event into collection or update existing one.

    Args:
        event: The event object which needs to be updated.

    Return: 
        True: Update complete.
        False: Exception occurred.
    '''

    try:

        if events_collection.find_one({'_id': str(event._id)}) != None:
            events_collection.replace_one({'_id': event._id}, event.toObject())
            return True
        else:
            events_collection.insert_one(event.toObject())
            return True

    except Exception as e:
        print(bcolors.FAIL + 'Exception occur when updating event:' + bcolors.ENDC)
        print(e)
        return False
