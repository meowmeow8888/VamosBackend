import hashlib
from os import environ


def user_id_to_topic(user_id):
    if user_id == -1:
        return "all"
    topic_pass = environ["TOPIC_PASS"]
    return hashlib.sha256(f"{user_id}{topic_pass}".encode()).hexdigest()
