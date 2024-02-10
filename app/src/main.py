import os

if True:
  from app_utils import get_packages, safe_jsonify
  print(safe_jsonify(get_packages()))
#endif

from fastapi import FastAPI, APIRouter, Request, File, UploadFile
from pydantic import BaseModel
from app_utils import boxed_print

app = FastAPI()
router_monitor= APIRouter()
router_serving = APIRouter()
router_basic_app = APIRouter()

app_type = os.environ.get('APP_TYPE', 'serving')


if app_type.lower() == 'serving':
  from serving.serving_app import ServingApp  
  eng = ServingApp()
elif app_type.lower() == 'monitor':
  from monitor.monitor_app import MonitorApp  
  eng = MonitorApp()
else:
  from basic_app.engine import AppHandler
  eng = AppHandler()
# end if select engine


####################
## Serving routes ##
####################

# string request
@router_serving.get("/predict/text")
async def predict_text(text: str):
  result = eng.predict_text(text)
  return {"result": result}

# json request
class Item(BaseModel):
  field1: str
  field2: str
  field3: str

@router_serving.post("/predict/data")
async def predict_data(item: Item):
  result = eng.predict_json(item.dict())
  return {"result": result}

# image request
@router_serving.post("/predict/image")
async def predict_image(image: UploadFile = File(...)):
  contents = await image.read()
  # Process the image data
  result = eng.predict_image(contents)
  return {"result": result}

@router_serving.get("/predict")
async def predict(text: str):
  result = eng.predict_text(text)
  return {"result": result}

@router_serving.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str):
  msg = "Received request on {} => redirected for catch-all".format(full_path)
  return {"result": msg}


####################
## Monitor routes ##
####################

@router_monitor.get("/health")
async def health():
  result = eng.get_health()
  return {"result": result}


@router_monitor.get("/modelconfig")
async def modelconfig(modeltype:str, modelname: str):
  result = eng.set_model(model_type=modeltype, model=modelname)
  return {"result": result}

@router_monitor.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str):
  msg = "Received request on {} => redirected for catch-all".format(full_path)
  return {"result": msg}


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
if app_type.lower() == 'serving':
  app.include_router(router_serving)
elif app_type.lower() == 'monitor':
  app.include_router(router_monitor)  
else:
  app.include_router(router_basic_app)
# end if select router for app type