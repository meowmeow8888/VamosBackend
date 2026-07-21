import hashlib
from base64 import b64encode
from os import environ


def user_id_to_topic(user_id):
    if user_id == -1:
        return "all"
    topic_pass = environ["TOPIC_PASS"]
    return b64encode(hashlib.sha256(str(user_id).encode() + topic_pass.encode()).digest()).decode()
