import os
from typing import Dict
from pydantic import BaseModel

if True:
  from app_utils import show_inventory
  show_inventory()
#endif


from fastapi import FastAPI, APIRouter
from app_utils import boxed_print

from monitor.monitor_app import MonitorApp  

app = FastAPI(root_path=os.getenv('ROOT_PATH', ''))
router_monitor= APIRouter()

eng = MonitorApp()

####################
## Monitor routes ##
####################

@router_monitor.get("/health")
async def health():
  result = eng.get_health()
  return result

class InferenceModel(BaseModel):
  modelname: str
  modeltype: str
  labels: Dict[str,str] =  None

class AppModule(BaseModel):
  cur_ver: str
  new_ver: str 


@router_monitor.post("/modelconfig")
async def modelconfig(model: InferenceModel ):
  result = eng.set_model(model_type=model.modeltype, model_name=model.modelname, labels=model.labels)
  return result

@router_monitor.post("/updatemonitor")
async def updatemonitor(app_module: AppModule ):
  result = eng.update_monitor(app_module.dict())
  return result

@router_monitor.post("/updateserving")
async def updateserving(app_module: AppModule ):
  result = eng.update_serving(app_module.dict())
  return result


@router_monitor.get("/{full_path:path}", include_in_schema=False)
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
app.include_router(router_monitor)  
