from SQL_ORM import Friend, Friend_of, Balance, Transaction, App_ORM

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

def get_friends_and_balances(name):
  db = App_ORM()
  friends = db.get_friends_of(name)
  balances = db.get_balances_for_friend_id(db.get_friend_id_by_name(name))
  friends_of = [Friend_of(f, b) for f, b in zip(friends, balances)]
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