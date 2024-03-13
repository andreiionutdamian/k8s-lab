import os

if True:
  from app_utils import show_inventory, format_result
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
  return format_result(result)


@router_monitor.get("/modelconfig")
async def modelconfig(modeltype:str, modelname: str):
  result = eng.set_model(model_type=modeltype, model=modelname)
  return format_result(result)

@router_monitor.get("/{full_path:path}", include_in_schema=False)
async def catch_all(full_path: str):
  msg = "Received request on {} => redirected for catch-all".format(full_path)
  return format_result(msg)



@app.on_event("startup")
async def startup_event():
  # rectangle-print Starting up the app
  msg = "Starting up {}".format(eng.__class__.__name__)
  boxed_print(msg)
  eng.setup()
  return

# router selection
app.include_router(router_monitor)  
