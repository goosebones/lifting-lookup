from typing import Union
import json
import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from liftingcast import lifters_output_filename


app = FastAPI()
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/lifters")
def get_lifters():
    if not os.path.exists(lifters_output_filename):
        lifters = []
    else:
        with open(lifters_output_filename, "r") as f:
            lifters = json.load(f)
    return json.dumps(lifters)


@app.get("/last-updated")
def get_last_updated():
    t = time.ctime(os.path.getmtime(lifters_output_filename))
    return t
