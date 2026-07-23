from SQL_ORM import *
import secrets
from handlers.notification_sender import NotificationBuilder


def get_highers(id, ids):
    highers = []
    for i in ids:
        if i > id:
            highers.append(i)
    return highers


def ensure_balances():
    db = App_ORM()
    ids = db.get_all_ids()
    for id in ids:
        balances = db.get_balances_for_friend_id(id)
        highers = get_highers(id, ids)
        if highers:
            for missing in highers:
                balance = Balance(id, missing, 0)
                if balance not in balances:
                    db.insert_balance(balance)


def get_friends(id):
    db = App_ORM()
    friends = db.get_friends_of(id)
    balances = db.get_balances_for_friend_id(id)

    friends_of = []
    for f, b in zip(friends, balances):
        if db.nickname_exists(id, f.friend_id):
            nickname = db.get_nickname(id, f.friend_id)
        else:
            nickname = Nickname(id, f.friend_id, "")
        friends_of.append(Friend_of(f, b, nickname))
    return friends_of


def handle_create_transaction(tx: Transaction):
    db = App_ORM()
    db.insert_transaction(tx)
    sender_name = db.get_name_by_friend_id(tx.sender_id)
    NotificationBuilder().with_user_id(
        tx.receiver_id).transaction_received(sender_name).build().send()


def handle_nickname(nickname: Nickname):
    db = App_ORM()
    if db.nickname_exists(nickname.nicker_id, nickname.nicked_id):
        db.update_nickname(nickname)
    else:
        db.insert_nickname(nickname)


def create_session(friend_id):
    session_id = secrets.token_hex(32)
    session = Session(session_id, friend_id)
    return session


def login(name, password):
    db = App_ORM()
    name = " ".join(name.split())
    if not db.friend_exists(name):
        db.insert_friend(Friend(0, name, password))
        ensure_balances()
    if not db.validate_friend(name, password):
        return None
    f_id = db.get_friend_id_by_name(name)
    session = create_session(f_id)
    db.insert_session(session)
    return session.session_id


def logout(session_id):
    db = App_ORM()
    db.delete_session(session_id)


def me(session_id):
    db = App_ORM()
    if not db.session_exists(session_id):
        return None
    return db.get_friend_id_from_session(session_id)
