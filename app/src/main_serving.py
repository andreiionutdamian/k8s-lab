import os

if True:
  from app_utils import show_inventory
  show_inventory()
#endif


from fastapi import FastAPI, APIRouter, File, UploadFile
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
  return {"result": result}


# string request
@router_serving.get("/predict/text")
async def predict_text(text: str):
  result = eng.predict_text(text)
  return {"result": result}

# TODO: predict json

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



@app.on_event("startup")
async def startup_event():
  # rectangle-print Starting up the app
  msg = "Starting up {}".format(eng.__class__.__name__)
  boxed_print(msg)
  eng.setup()
  return

# router selection
app.include_router(router_serving)
