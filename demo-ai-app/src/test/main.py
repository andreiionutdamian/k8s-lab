import os
import json
from uuid import uuid4
from fastapi import FastAPI, APIRouter, Query

hostname = os.getenv('HOSTNAME', 'unknown')
local_id = "demo-ai-app-" + str(uuid4()[:5])

# redis_host = os.getenv('REDIS_SERVICE_HOST')
# redis_port = os.getenv('REDIS_SERVICE_PORT')
# redis_password = os.getenv('REDIS_PASSWORD')

# postgres_host = os.getenv('POSTGRES_SERVICE_HOST')

dct_env = {
  k : v for k, v in os.environ.items() 
  if k.startswith("REDIS_" or k.startswith("POSTGRES_"))
} 
print(json.dumps(dct_env, indent=2))

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": f"Hello from {hostname} <{local_id}>!"}