import os
import json

if True:
  from app_utils import show_inventory
  show_inventory()
#endif

from typing import List, Optional, Annotated
from fastapi import FastAPI, APIRouter, File, UploadFile, Form, Body
from pydantic import BaseModel
from app_utils import boxed_print

from serving.serving_app import ServingApp  

app = FastAPI(root_path=os.getenv('ROOT_PATH', ''))
router_serving = APIRouter()

eng = ServingApp()


####################
## Serving routes ##
####################

@router_serving.get("/health")
async def health():
  result = eng.get_health()
  return result

class ExecParams(BaseModel):
  device: Optional[str] = None
  no_runs: Optional[int] = None


# string request
@router_serving.post("/predict/text")
async def predict_text(
  text: str = Annotated[str, Body()], 
  exec_params: Optional[ExecParams] = None
):
  params = exec_params.dict() if exec_params else None
  result = eng.predict_text(text, params)
  return result

@router_serving.post("/predict/texts")
async def predict_texts(
  texts: List[str], 
  exec_params: Optional[ExecParams] = None
):
  params = exec_params.dict() if exec_params else None
  result = eng.predict_texts(texts, params)
  return result

# TODO: predict json

# json request
class Item(BaseModel):
  input_field1: str
  input_field2: str
  input_field3: str

@router_serving.post("/predict/data")
async def predict_data(
  item: Item, 
  exec_params: Optional[str] = Form(None)
):
  params = json.loads(exec_params) if exec_params else None
  result = eng.predict_json(item.dict(), params)
  return result

# image request
@router_serving.post("/predict/image")
async def predict_image(
  image: UploadFile = File(...), 
  exec_params: Optional[ExecParams] = None
):
  contents = await image.read()
  params = exec_params.dict() if exec_params else None
  # Process the image data
  result = eng.predict_image(contents, params)
  return result

@router_serving.post("/predict")
async def predict(
  text: str , 
  exec_params: Optional[ExecParams] = None
):
  params = exec_params.dict() if exec_params else None
  result = eng.predict_text(text, params)
  return result

@router_serving.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str):
  msg = "Received request on {} => redirected for catch-all".format(full_path)
  return msg

@app.on_event("startup")
async def startup_event():
  # rectangle-print Starting up the app
  msg = "Starting up {}".format(eng.__class__.__name__)
  boxed_print(msg)
  eng.setup()
  return

# router selection
app.include_router(router_serving)
