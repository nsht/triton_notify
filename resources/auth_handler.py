import datetime
import logging
import pdb

from flask import current_app as app
from flask import request
from resources.constants import *
from flask_restful import abort
import jwt
import bcrypt

from models.models import User


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
        payload = jwt.decode(auth_token, SECRET_KEY)
        return payload["sub"]
    except jwt.ExpiredSignatureError:
        app.logger.error(
            f"{datetime.datetime.utcnow().isoformat()} |Signature Expired | {request.remote_addr}"
        )
        return "Signature Expired"
    except jwt.InvalidTokenError:
        app.logger.error(
            f"{datetime.datetime.utcnow().isoformat()} |Invalid token| {request.remote_addr}"
        )
        return "Invalid token"


def validate_auth_token(func):
    def inner(*args, **kwargs):
        auth_header = request.headers.get('Authorization',"")
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            abort(401,message='Bearer token malformed')
        print(auth_token)
        token_data = decode_auth_token(auth_token)
        if isinstance(token_data, str):
            abort(401, message=f"Invalid Token")
        else:
            return func(*args, **kwargs)

    return inner


def do_login(username, password):
    if username == False or password == False:
        return False

    user = User.query.filter_by(username=username).first()
    if not user:
        return False

    # Redudant check since user object is fetched by username
    if user.username != username:
        return False
    if bcrypt.hashpw(password.encode(), user.password) != user.password:
        return False

    return True

