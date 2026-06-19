from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from handlers.balance_handler import ensure_balances, get_friends_and_balances, handle_transaction, get_my_id
from SQL_ORM import App_ORM, Transaction
from pydantic import BaseModel

class TransactionRequest(BaseModel):
  senderId: int
  receiverId: int
  amount: float

ensure_balances()

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
    friends_and_balances = get_friends_and_balances(name)
    return {"friends": friends_and_balances}

@app.get("/api/id")
def api_id(name):
    id = get_my_id(name)
    return {"id": id}

@app.post("/api/transactions")
def api_transactions(tx: TransactionRequest):
    print(tx.senderId, tx.receiverId, tx.amount)
    if tx.amount > 0:
        transaction = Transaction(0, tx.receiverId, tx.senderId, tx.amount)
    else:
       transaction = Transaction(0, tx.senderId, tx.receiverId, -tx.amount)
    handle_transaction(transaction)
    return {}