from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from handlers.balance_handler import ensure_balances, get_friends_and_balances, handle_transaction
from SQL_ORM import App_ORM, Transaction
from pydantic import BaseModel

class TransactionRequest(BaseModel):
  senderId: int
  receiverId: int
  amount: float

db = App_ORM()
ensure_balances(db)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/friends")
def api_friends(name):
    friends_and_balances = get_friends_and_balances(db, name)
    return {"friends": friends_and_balances}

@app.get("/api/id")
def api_id(name):
    id = db.get_friend_id_by_name(name)
    return {"id": id}

@app.post("/api/transactions")
def api_transactions(tx: TransactionRequest):
    if tx.amount > 0:
        transaction = Transaction(0, tx.receiverId, tx.senderId, tx.amount)
    else:
       transaction = Transaction(0, tx.senderId, tx.receiverId, tx.amount)
    handle_transaction(db, transaction)
    return {}