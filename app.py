import pdb

from flask import Flask, request, make_response
from flask_restful import Resource, Api,abort

app = Flask(__name__)
api = Api(app)

MESSAGE_TYPES = ["telegram", "email", "sms", "log", "twitter"]


class Test(Resource):
    def get(self):
        return "{'hello':'test'}"


class Message(Resource):
    def post(self,message_type):
        if message_type not in MESSAGE_TYPES:
            abort(404, message=f"Invalid message type {message_type}")
        print(message_type)
        print(request.json)
        return {"status":"ok"}

api.add_resource(Test,'/')
api.add_resource(Message,'/message/<string:message_type>')


if __name__ == "__main__":
    app.run()
