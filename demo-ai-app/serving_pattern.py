from time import sleep
from fastapi import FastAPI, APIRouter, Request, File, UploadFile
from threading import Thread
from pydantic import BaseModel


class ModelServer:
  def __init__(self, **kwargs):
    self.__done = False
    return
  
  def checker_loop(self):
    while not self.__done:
      # check for models
      sleep(1)
    return
  
  def start(self):
    self.__done = False
    thread = Thread(target=self.checker_loop, daemon=True)
    thread.start()
    self.__thread = thread
    return
  
  def shutdown(self):
    self.__done = True
    return
  
  
  def predict(self, data):
    result = None
    return result
  
engine = ModelServer()
app = FastAPI()
router = APIRouter()

@app.on_event("startup")
async def on_startup():
  engine.start()
  return

@app.on_event("shutdown")
async def on_shutdown():
  engine.shutdown()
  return

# json request
class Item(BaseModel):
  field1: str
  field2: str
  field3: str

@app.post("/predict2")
async def predict2(item: Item):
  return {"message": f"Received JSON body: {item}"}
  
  
# image request
@app.post("/predict3")
async def predict3(image: UploadFile = File(...)):
  contents = await image.read()
  # Process the image data
  return {"message": "Image received"}  
  

# universal request
@router.post("/predict")
async def predict_universal(request: Request):
  content_type = request.headers.get("content-type")

  if content_type == "application/json":
    # Handle JSON request
    json_body = await request.json()
    return {"message": f"Received JSON body: {json_body}"}
  elif content_type == "image/jpeg" or content_type == "image/png":
    # Handle image upload
    image = await request.body()
    # Process the image data
    return {"message": "Image received"}
  else:
    # Assume it's a plain text request
    text_body = await request.body()
    return {"message": f"Received plain text body: {text_body.decode()}"}

app.include_router(router)