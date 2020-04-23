# -*- coding: utf-8 -*-

from db import sessions_collection


def checksession(session):
    check_result = sessions_collection.find_one({"_id": session})
    if check_result != None:
        return True
    else:
        return False
