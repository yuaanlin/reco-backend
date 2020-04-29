from db import repeats_collection

from utils.bcolors import bcolors


def update_repeat(repeat):
    '''Create a new repeat into collection or update existing one.

    Args: 
        repeat: The repeat object which needs to be updated.

    Return:
        True: Update complete.
        False: Exception occurred.
    '''

    try:

        if repeats_collection.find_one({'_id': repeat['_id']}) != None:
            repeats_collection.replace_one({'_id': repeat['_id']}, repeat)
            return True
        else:
            repeats_collection.insert_one(repeat)
            return True

    except Exception as e:
        print(bcolors.FAIL + 'Exception occur when updating todo:' + bcolors.ENDC)
        print(e)
        return False
