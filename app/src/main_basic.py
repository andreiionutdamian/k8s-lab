import os

if True:
  from app_utils import get_packages, safe_jsonify
  print(safe_jsonify(get_packages()))
#endif

from fastapi import FastAPI, APIRouter
from app_utils import boxed_print

from basic_app.engine import AppHandler


app = FastAPI()
router_basic_app = APIRouter()

eng = AppHandler()


######################
## Basic App routes ##
######################

@router_basic_app.get("/")
# async def root(data: str = Query(...)): # this makes the `data` parameter mandatory
async def root(data: str = None):
  print("Received request for root with params: ", data)
  return eng.handle_request("/", parameter=data)

@router_basic_app.get("/stats")
async def stat(data: str = None):
  print("Received request for stat with params: ", data)
  return eng.handle_request("/", parameter=data)

# note: this is a catch-all route, so it should be the last route in the router
@router_basic_app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str, data: str = None):
  print("Received request for catch-all with params: ", data)
  return eng.handle_request(full_path, parameter=data)


@app.on_event("startup")
async def startup_event():
  # rectangle-print Starting up the app
  msg = "Starting up {}".format(eng.__class__.__name__)
  boxed_print(msg)
  eng.setup()
  return

# router selection
app.include_router(router_basic_app)
