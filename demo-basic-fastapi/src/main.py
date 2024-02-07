import os
from uuid import uuid4
from fastapi import FastAPI, APIRouter, Query
from engine import AppHandler, AppPaths


engine = AppHandler()
app = FastAPI()
router1 = APIRouter()

ROUTE1 = AppPaths.PATH_ROOT['PATH']
@router1.get(ROUTE1)
async def root(parameter: str = Query(...)):
  return engine.handle_request(ROUTE1, parameter=parameter)

ROUTE2 = AppPaths.PATH_STAT['PATH']
@router1.get(ROUTE2)
async def stat(parameter: str = Query(...)):
  return engine.handle_request(ROUTE2, parameter=parameter))

# note: this is a catch-all route, so it should be the last route in the router
@router1.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str, parameter: str = Query(...)):
  return engine.handle_request(full_path, parameter=parameter)
  

app.include_router(router1)
