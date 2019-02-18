from flask import Flask, request, make_response

app = Flask(__name__)
MESSAGE_TYPES = ["telegram", "email", "sms", "log", "twitter"]


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/message/<message_type>", methods=["POST"])
def send(message_type):
    print(request.json)
    request_object = request.json
    if request_object.get("message"):
        print(request_object["message"])
    if message_type not in MESSAGE_TYPES:
        return make_response("Type not found", 404)
    return f"{message_type} sent successfully"


if __name__ == "__main__":
    app.run()
