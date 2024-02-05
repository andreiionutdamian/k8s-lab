import os
from uuid import uuid4
from fastapi import FastAPI

str_local_id = "test_" + str(uuid4())[:5]
hostname = os.environ.get("HOSTNAME", "unknown")

print("Initializing FastAPI app with ID: , HOSTNAME: {}...", str_local_id, hostname)

app = FastAPI()

@app.get("/")
async def root():
  msg = f"Hello world from HOSTNAME: '{hostname}', ID: '{str_local_id}'\n"
  return {"message": msg}