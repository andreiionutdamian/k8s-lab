import os
from fastapi import FastAPI, APIRouter, Request, File, UploadFile


app = FastAPI()
router = APIRouter()

app_type = os.environ.get('APP_TYPE', 'serving')


if app_type.lower() == 'serving':
  from serving import ServingApp
  
  eng = ServingApp()

  @router.post("/predict")
  async def predict_image(file: UploadFile = File(...)):
      return predict(file)
else:
  from monitor import MonitorApp
  
  eng = MonitorApp()
