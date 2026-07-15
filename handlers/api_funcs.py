from SQL_ORM import *
import secrets


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


def get_friends(name):
    db = App_ORM()
    myId = db.get_friend_id_by_name(name)
    friends = db.get_friends_of(name)
    balances = db.get_balances_for_friend_id(myId)

    friends_of = []
    for f, b in zip(friends, balances):
        if db.nickname_exists(myId, f.friend_id):
            nickname = db.get_nickname(myId, f.friend_id)
        else:
            nickname = Nickname(myId, f.friend_id, "")
        friends_of.append(Friend_of(f, b, nickname))
    return friends_of


def handle_transaction(tx: Transaction):
    db = App_ORM()
    db.insert_transaction(tx)
    if tx.payer_id > tx.receiver_id:
        db.update_balance(tx.receiver_id, tx.payer_id, tx.amount)
    else:
        db.update_balance(tx.payer_id, tx.receiver_id, -tx.amount)


def get_my_id(name):
    db = App_ORM()
    return db.get_friend_id_by_name(name)


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
    if not db.friend_exists(name):
        db.insert_friend(Friend(0, name, password))
    if not db.validate_friend(name, password):
        return None
    f_id = db.get_friend_id_by_name(name)
    session = create_session(f_id)
    db.insert_session(session)
    return session.session_id


def me(session_id):
    db = App_ORM()
    if not db.session_exists(session_id):
        return None 
    return db.get_friend_id_from_session(session_id)


if __name__ == '__main__':
    db = App_ORM()

    db.delete_table("friends")
    db.delete_table("balances")

    db._ensure_tables()

    db.insert_friend(Friend(0, "Guy Mosseri"))
    db.insert_friend(Friend(0, "Orr Sarid"))
    db.insert_friend(Friend(0, "Tamar Price"))
    db.insert_friend(Friend(0, "Dror Krieze"))
    db.insert_friend(Friend(0, "Mia shuster"))
    print("inserted new friends")

    ensure_balances(db)
    print("created balances")
