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
        "sub": user_id,
    }
    try:
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256").decode()
        return token
    except Exception as e:
        app.logger.error(
            f"{datetime.datetime.utcnow().isoformat()} |Error generating token:{e} | {request.remote_addr}"
        )
        return

def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token,SECRET_KEY)
        return payload['sub']
    except jwt.ExpiredSignatureError:
        app.logger.error(
            f"{datetime.datetime.utcnow().isoformat()} |Signature Expired | {request.remote_addr}"
        )
        return 'Signature Expired'
    except jwt.InvalidTokenError:
        app.logger.error(
            f"{datetime.datetime.utcnow().isoformat()} |Invalid token| {request.remote_addr}"
        )
        return 'Invalid token'

def validate_auth_token(func):
    def inner(*args,**kwargs):
        auth_token = request.json.get("auth_token", "NA")
        token_data = decode_auth_token(auth_token)
        print(token_data)
        if isinstance(token_data,str):
            abort(401, message=f"Invalid Token")
        else:
            return func(*args, **kwargs)
    return inner

