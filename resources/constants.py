import os


MESSAGE_TYPES = ["telegram", "email", "sms", "log", "twitter"]
SECRET_KEY = os.getenv('SECRET_KEY', 'my_precious')