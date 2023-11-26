from typing import Union
import json
import os
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from liftingcast import lifters_output_filename

lifter_file = os.path.join(os.path.dirname(__file__), lifters_output_filename)


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
    if not os.path.exists(lifter_file):
        lifters = []
    else:
        with open(lifter_file, "r") as f:
            lifters = json.load(f)
    return json.dumps(lifters)


@app.get("/last-updated")
def get_last_updated():
    if not os.path.exists(lifter_file):
        return None
    t = time.ctime(os.path.getmtime(lifter_file))
    return t
