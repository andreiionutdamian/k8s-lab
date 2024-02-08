import os
from uuid import uuid4
from fastapi import FastAPI, APIRouter, Query
from engine import AppHandler, AppPaths


engine = AppHandler()
app = FastAPI()
router1 = APIRouter()

@app.on_event("startup")
async def startup_event():
  print("Starting up {}...".format(engine.__class__.__name__))
  engine.setup()
  return

ROUTE1 = AppPaths.PATH_ROOT['PATH']
@router1.get(ROUTE1)
# async def root(data: str = Query(...)): # this makes the `data` parameter mandatory
async def root(data: str = None):
  print("Received request for root with params: ", data)
  return engine.handle_request(ROUTE1, parameter=data)

ROUTE2 = AppPaths.PATH_STAT['PATH']
@router1.get(ROUTE2)
async def stat(data: str = None):
  print("Received request for stat with params: ", data)
  return engine.handle_request(ROUTE2, parameter=data)

# note: this is a catch-all route, so it should be the last route in the router
@router1.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str, data: str = None):
  print("Received request for catch-all with params: ", data)
  return engine.handle_request(full_path, parameter=data)
  

app.include_router(router1)
