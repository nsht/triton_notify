import pdb
import datetime
import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, request, make_response
from flask_restful import Resource, Api, abort
from flask_sqlalchemy import SQLAlchemy

from resources.telegram import Telegram


app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)


class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    email_id = db.Column(db.String(120), unique=True, nullable=False)
    date_created = db.Column(
        db.TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.utcnow
    )
    last_login = db.Column(db.TIMESTAMP(timezone=True))
    status = db.Column(db.Integer, nullable=False)
    user_permissions = db.relationship("UserPermissions ", backref="user", lazy=True)

    def __repr__(self):
        return f"Username: {self.username}"

class Permissions(db.Model):
    perm_id = db.Column(db.Integer, primary_key=True)
    perm_name = db.Column(db.String(50), unique=True, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    date_created = db.Column(
        db.TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.utcnow
    )

    def __repr__(self):
        return f"Permission: {perm_name}"


class UserPermissions(db.Model):
    uperm_id = db.Column(db.Integer, primary_key=True)
    perm_id = db.Column(db.Integer, db.ForeignKey("permissions.perm_id"), nullable=False)
    status = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.uid"), nullable=False)
    access_granted_on = db.Column(
        db.TIMESTAMP(timezone=True), nullable=False, default=datetime.datetime.utcnow
    )

    def __repr__(self):
        return f"Permission{perm_id}, User={user_id}"


# Adds RotatingFileHandler if app is not running on aws lambda
# Since labda instances are read only RotatingFileHandler won't work
# In lambda logs and print statements are added to aws cloudwatch logs
if os.environ.get("AWS_EXECUTION_ENV") == None:
    handler = RotatingFileHandler("app.log", maxBytes=10000, backupCount=3)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)

api = Api(app)

MESSAGE_TYPES = ["telegram", "email", "sms", "log", "twitter"]
MESSAGE_PROVIDERS = {"telegram": Telegram}


class Index(Resource):
    def get(self):
        return "ok", 200


class HealthCheck(Resource):
    def get(self):
        app.logger.info(
            f"{datetime.datetime.utcnow().isoformat()} | HealthCheck done | {request.remote_addr}"
        )
        return {"status": "ok"}, 200


class Message(Resource):
    def post(self, message_type):
        if message_type not in MESSAGE_TYPES:
            app.logger.error(
                f"{datetime.datetime.utcnow().isoformat()} | Invalid message type:{message_type} | {request.remote_addr}"
            )
            abort(404, message=f"Invalid message type {message_type}")
        message_provider = MESSAGE_PROVIDERS.get(message_type)(request.json, request)
        message_status = message_provider.send_message()
        return message_status, message_status["status_code"]


api.add_resource(Index, "/")
api.add_resource(Message, "/message/<string:message_type>")
api.add_resource(HealthCheck, "/healthcheck")

if __name__ == "__main__":
    app.run()
