import datetime
import logging

from flask import current_app as app
from flask import request
from resources.constants import *
from flask_restful import abort
import jwt


def check_message_type(func):
    def inner(*args, **kwargs):
        message_type = kwargs.get("message_type", "NA")
        if kwargs.get("message_type", False) and kwargs.get("message_type") in MESSAGE_TYPES:
            return func(*args, **kwargs)
        else:
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | Invalid message type:{message_type} | {request.remote_addr}"
            )
            abort(404, message=f"Invalid message type {message_type}")

    return inner


def create_auth_token(user_id):
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow(),
        "user_id": user_id,
    }
    try:
        # TODO change secret to actual secret string stored in env variables
        token = jwt.encode(payload, "secret", algorithm="HS256").decode()
        return token
    except Exception as e:
        app.logger.error(
            f"{datetime.datetime.utcnow().isoformat()} |Error generating token:{e} | {request.remote_addr}"
        )
        return
