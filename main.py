from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from SQL_ORM import App_ORM, Friend_of

db = App_ORM()
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
    friends = db.get_friends_of(name)
    balances = db.get_balances_for_friend_id(db.get_friend_id_by_name(name))
    friends_of = [Friend_of(f, b) for f, b in zip(friends, balances)]
    return {"friends": friends_of}
