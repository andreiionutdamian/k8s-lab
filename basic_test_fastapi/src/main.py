import os
from uuid import uuid4
from fastapi import FastAPI, APIRouter
from engine import AppHandler, AppPaths


engine = AppHandler()
app = FastAPI()
router1 = APIRouter()

@router1.get(AppPaths.PATH_ROOT['PATH'])
async def root():
  return engine.handle_request(AppPaths.PATH_ROOT['PATH'])

@router1.get(AppPaths.PATH_STAT['PATH'])
async def stat():
  return engine.handle_request(AppPaths.PATH_STAT['PATH'])

# note: this is a catch-all route, so it should be the last route in the router
@router1.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str):
  return engine.handle_request(full_path)
  


app.include_router(router1)
