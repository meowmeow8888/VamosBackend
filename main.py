from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from SQL_ORM import App_ORM

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
    friends = db.get_friends(name)
    return {"friends": friends}
