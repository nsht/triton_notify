import datetime
import logging

from flask import current_app as app
from flask import request
from resources.constants import *
from flask_restful import abort

def check_message_type(func):
    def inner(*args, **kwargs):
        import pdb; pdb.set_trace()
        message_type = kwargs.get("message_type", "NA")
        if kwargs.get("message_type", False) and kwargs.get("message_type") in MESSAGE_TYPES:
            print(*args)
            print("deco running")
            return func(*args, **kwargs)
        else:
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | Invalid message type:{message_type} | {request.remote_addr}"
            )
            abort(404, message=f"Invalid message type {message_type}")

    return inner