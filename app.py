import pdb

from flask import Flask, request, make_response
from flask_restful import Resource, Api, abort
from resources.telegram import Telegram

app = Flask(__name__)
api = Api(app)

MESSAGE_TYPES = ["telegram", "email", "sms", "log", "twitter"]
MESSAGE_PROVIDERS = {'telegram':Telegram}
class Test(Resource):
    def get(self):
        return "{'hello':'test'}"


class Message(Resource):
    def post(self, message_type):
        if message_type not in MESSAGE_TYPES:
            abort(404, message=f"Invalid message type {message_type}")
        message_provider = MESSAGE_PROVIDERS.get(message_type)(request.json)
        message_status = message_provider.send_message()
        return message_status['status_message'],message_status['status_code']


api.add_resource(Test, "/")
api.add_resource(Message, "/message/<string:message_type>")


if __name__ == "__main__":
    app.run()
