import os
from uuid import uuid4
from fastapi import FastAPI, APIRouter

str_local_id = "test_" + str(uuid4())[:5]
hostname = os.environ.get("HOSTNAME", "unknown")

print("Initializing FastAPI app with ID: , HOSTNAME: {}...", str_local_id, hostname)

app = FastAPI()
router1 = APIRouter()
router2 = APIRouter()

PATH_1 = "/"
@router1.get(PATH_1)
async def root():
  msg = f"Handler '{PATH_1}', Worker HOSTNAME: '{hostname}', ID: '{str_local_id}'\n"
  return {"message": msg}

# note: this is a catch-all route, so it should be the last route in the router
@router1.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str):
  msg = f"Generic handler on path:{full_path}, Worker HOSTNAME: '{hostname}', ID: '{str_local_id}'\n"
  return {"message": msg}


app.include_router(router1)
