import datetime
import logging
import pdb

from flask import current_app as app
from flask import request
from flask_restful import abort
import jwt
import bcrypt

from triton_notify.resources.constants import *


from triton_notify.models.models import db, User, Permissions, UserPermissions


def check_message_type(func):
    def inner(*args, **kwargs):
        message_type = kwargs.get("message_type", "NA")
        if (
            kwargs.get("message_type", False)
            and kwargs.get("message_type") in MESSAGE_TYPES
        ):
            return func(*args, **kwargs)
        else:
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | Invalid message type:{message_type} | {request.remote_addr}"
            )
            abort(404, message=f"Invalid message type {message_type}")

    return inner


def check_user_permissions(func):
    def inner(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        auth_token = auth_header.split(" ")[1]
        payload = jwt.decode(auth_token, SECRET_KEY)
        permissions = payload.get("permissions").split(",")
        message_type = kwargs.get("message_type")
        if message_type in permissions:
            return func(*args, **kwargs)
        else:
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | Insufficient Permission {message_type} for user:{payload['sub']} | {request.remote_addr}"
            )
            abort(401, message=f"Insufficient Permissions")

    return inner


def create_auth_token(user_id):
    permission_data = (
        db.session.query(User, Permissions, UserPermissions)
        .filter(User.uid == UserPermissions.user_id)
        .filter(Permissions.perm_id == UserPermissions.perm_id)
        .filter(User.uid == user_id)
    )
    permission_list = [x.Permissions.perm_name for x in permission_data]
    payload = {
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
        "iat": datetime.datetime.utcnow(),
        "sub": user_id,
        "permissions": ",".join(permission_list),
    }
    print(payload)
    try:
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256").decode()
        app.logger.info(
            f"{datetime.datetime.utcnow().isoformat()} | Auth token generated for uid:{user_id} | {request.remote_addr}"
        )
        return token
    except Exception as e:
        app.logger.error(
            f"{datetime.datetime.utcnow().isoformat()} |Error generating token:{e} | {request.remote_addr}"
        )
        return


def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, SECRET_KEY)
        app.logger.info(
            f"{datetime.datetime.utcnow().isoformat()} | Token Decoded for uid {payload['sub']} | {request.remote_addr}"
        )
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
        auth_header = request.headers.get("Authorization", "")
        try:
            auth_token = auth_header.split(" ")[1]
        except IndexError:
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | Bearer token malformed | {request.remote_addr}"
            )
            abort(401, message="Bearer token malformed")
        print(auth_token)
        token_data = decode_auth_token(auth_token)
        # Change isistance check to boolean check
        if isinstance(token_data, str):
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | Invalid Token | {request.remote_addr}"
            )
            abort(401, message=f"Invalid Token")
        else:
            return func(*args, **kwargs)

    return inner


def do_login(username, password):
    if username == False or password == False:
        app.logger.error(
            f"{datetime.datetime.utcnow().isoformat()} | Failed Login No username or password for: {username} | {request.remote_addr}"
        )
        return False

    user = User.query.filter_by(username=username).first()
    if not user:
        app.logger.error(
            f"{datetime.datetime.utcnow().isoformat()} | Failed Login username not found for: {username} | {request.remote_addr}"
        )
        return False

    # Redudant check since user object is fetched by username
    if user.username != username:
        return False
    if bcrypt.hashpw(password.encode(), user.password) != user.password:
        app.logger.error(
            f"{datetime.datetime.utcnow().isoformat()} | Failed Login invalid password for: {username} | {request.remote_addr}"
        )
        return False
    app.logger.info(
        f"{datetime.datetime.utcnow().isoformat()} | Login Successfull for: {username} | {request.remote_addr}"
    )
    return True
