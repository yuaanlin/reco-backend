from db import todos_collection


def update_todo(todo):
    '''Create a new Todo into collection or update existing one.

    Args: 
        todo: The todo object which needs to be updated.

    Return:
        True: Update complete.
        False: Exception occurred.
    '''

    try:

        if todos_collection.find_one({'_id': todo['_id']}) != None:
            todos_collection.replace_one(
                {'_id': todo['_id']}, todo)
            return True
        else:
            todos_collection.insert_one(todo)
            return True

    except:
        return False
