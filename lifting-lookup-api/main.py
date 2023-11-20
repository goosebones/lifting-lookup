from typing import Union
import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lookup import get_all_lifters

lifters = get_all_lifters()


app = FastAPI()
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}


@app.get("/lifters")
def get_lifters():
    return json.dumps(lifters)
