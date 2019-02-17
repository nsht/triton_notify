from flask import Flask, make_response

app = Flask(__name__)
MESSAGE_TYPES = ["telegram", "email", "sms", "log", "twitter"]


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/test/<name>")
def test(name):
    return f"Hey {name}"


@app.route("/send/<message_type>", methods=["GET", "POST"])
def send(message_type):
    if message_type not in MESSAGE_TYPES:
        return make_response("Type not found", 404)
    return f"{message_type} sent successfully"


if __name__ == "__main__":
    app.run()
