import os
import io
import json
import time
import uuid

from typing import List
from PIL import Image

from mixins.base_mixin import _BaseMixin
from mixins.postgres_mixin import _PostgresMixin
from mixins.redis_mixin import _RedisMixin
from mixins.llm_mixin import _LlmMixin

STATUS_CREATED = 0
STATUS_ASSIGNED = 1
STATUS_INPROGRESS = 2
STATUS_FINISHED = 3
STATUS_RETRIEVED = 4

class ServingApp(
  _LlmMixin,
  _PostgresMixin,
  _RedisMixin,
  _BaseMixin,
  ):
  
  def __init__(self, **kwargs):
    super(ServingApp, self).__init__()
    self.no_predictions = 0
    self.log = None
    self.__available =  True
    self.__input = None
    return
  
  def setup(self):
    super(ServingApp, self).setup()    
    # setup serving
    self.models = {
      'text' : None,
      'json' : None,
      'image' : None,
    }

    self.output_labels = {
      'text' : None,
      'json' : None,
      'image' : None,
    }

    self.pipes = {
      "cpu": {
        'text' : None,
        'json' : None,
        'image' : None,
      },
      "gpu": {
        'text' : None,
        'json' : None,
        'image' : None,
      }
    }
    return
  
  
  def appmon_callback(self):
    super(ServingApp, self).appmon_callback()

    if (self.__available):
      task = None
      self.postgres_start_transaction()
      # search preassigned tasks
      assigned_tasks = self.postgres_select_data_ordered(
        "tasks", 
        for_update=True, order_by=None,order=None, maxrows=1,
        workername=self.host,status=STATUS_ASSIGNED
      )
      if assigned_tasks:
        task =  assigned_tasks[0]
        taskid = task[0]
        self.postgres_update_data("tasks",{"uuid":taskid},status=2) #transaction commited
      else:
        # try unnassigned tasks
        unassigned_tasks = self.postgres_select_data_ordered(
          "tasks", 
          for_update=True, order_by=None,order=None, maxrows=1,
          status=STATUS_CREATED
        )
        if unassigned_tasks:
          task =  unassigned_tasks[0]
          taskid = task[0]
          jobid = task[1]
          self.postgres_update_data("tasks",{"uuid":taskid},workername=self.host, status=STATUS_INPROGRESS) #transaction commited
          self.postgres_update_data("jobs",{"uuid":jobid},status=STATUS_ASSIGNED)
        else :
          #end transaction
          self.postgres_end_transaction()

      if task:
        self.__available = False
        taskid = task[0]
        jobid = task[1]
        result = None
        self.P(f"Processing task {taskid}")
        jobs = self.postgres_select_data("jobs",for_update=False, uuid=jobid)

        if jobs:
          job = jobs[0]
          model_type=job[2]
          device = job[3]
          no_runs = job[4]

          input = self.__input
          if input is None:
            # try loading from disk
            task_content_path = self.cache_root+"/tasks/"+taskid+".bin"
            try:
              with open(task_content_path, 'rb') as file:
                input = file.read()
            except Exception as exc:
              self.P("Content file read error: {}".format(exc))
          if input is not None:
            # convert if necessary
            if model_type == 'text':
              input_str = input.decode('utf-8')
              try:
                #check if list
                input = json.loads(input_str)
              except json.JSONDecodeError:
                input = input_str

            result = self._predict(
              model_type,
              input, 
              {"device":device, "no_runs":no_runs}
            )
          else:
            result = self.format_result("Input not available", device)
        else:
          result = self.format_result(
            result=f"Parent job not found: {jobid}"
          )

        self.postgres_update_data(
          table_name="tasks",
          identifier={"uuid":taskid}, 
          predict_date = time.strftime("%Y-%m-%d %H:%M:%S"),
          result=json.dumps(result), 
          status=STATUS_FINISHED
        )
        self.postgres_update_data(
          table_name="jobs",
          identifier={"uuid":jobid},
          status=STATUS_FINISHED
        )
        self.__available = True
    return
  
  def postgres_get_tables(self):
    tables ={
      "predicts" : "id SERIAL PRIMARY KEY, predict_date varchar(50), result varchar(255)",
      "jobs" : "uuid varchar(32) PRIMARY KEY, job_date varchar(50), model_type varchar(10), device varchar(10), no_runs integer, paralel_run boolean, batch_size int, status int",
      "tasks" : "uuid varchar(32) PRIMARY KEY, jobid varchar(32), workername varchar(50), predict_date varchar(50), result json, status int"
    }
    return tables

  
#  def __load_model(self, model_type: str, model_name: str):
#    # load models 
#   return
  
  
  def maybe_setup_models(self):
    # get models from Redis if available
    redis_models = self.redis_gethash("models")
    if len(redis_models) > 0:
      for k in self.models:
        self.maybe_setup_model(k)
    return
  
  def _get_device(self, target_device:str = None):
    device = target_device if target_device else self.get_default_device()
    if target_device == "gpu" and self.get_default_device() == "cpu":
      device = "cpu"
    if device == "cuda:0":
      device = "gpu"
    return device
  

  def maybe_setup_model(self, model_type:str, target_device:str = None):
    # get models from Redis if available
    redis_model = self.redis_hget("models", model_type)
    if redis_model is not None  and redis_model is not "":
      self.models[model_type] = redis_model
      redis_labels = self.redis_hget("labels", redis_model)
      if redis_labels:
        self.output_labels[model_type] = json.loads(redis_labels)
        self.P(f"Output lables loaded {self.output_labels[model_type]}")
      if os.path.exists(self.cache_root+"/"+redis_model):
        pipeline = self.load_model(model_type, redis_model, True, target_device)
        device = self._get_device(target_device)
        self.pipes[device][model_type]=pipeline
      else:
        raise Exception("Model not initialized") 
      # now mark as "seen"
      # self.redis_sethash("models", model_type, "")
    return
  
  def save_state_to_db(self, result):
    # TODO: is this safe for multi worker? - YES
    to_save = str(result)[:255]
    predict_date =time.strftime("%Y-%m-%d %H:%M:%S")
    # save result to Postgres
    self.postgres_insert_data("predicts", result=to_save, predict_date=predict_date)
    return
  
  def get_model(self, model_type: str,target_device:str = None):
    # get model from Redis
    redis_model = self.redis_hget("models", model_type)
    model = self.models[model_type]
    if redis_model is not None and ( model is None or model != redis_model) :
      try:
        device = self._get_device(target_device)
        self.maybe_setup_model(model_type, device) # only missing models should be loaded not all
        model = self.models[model_type]
      except Exception as exc:
        self.P("Error loading model: {}".format(exc))
    return model
  
  def get_pipeline(self, model_type: str, target_device:str = None):
    device = self._get_device(target_device)
    pipe = self.pipes[device][model_type]
    if pipe is None:
      try:
        self.maybe_setup_model(model_type, device) # only missing models should be loaded not all
        pipe = self.pipes[device][model_type]
      except Exception as exc:
        self.P("Error loading model: {}".format(exc))
    return pipe
  
  def _output_labels (self, model_type:str, result:list):
    if self.output_labels[model_type] is not None:
      self.P(f"converting labels using {self.output_labels[model_type]}")
      key_mapping = self.output_labels[model_type]
      output = []
      for result_item in result:
        self.P(f"for item {result_item}")
        for key in result_item :
          if result_item[key] in key_mapping:
            result_item[key] = key_mapping[result_item[key]]
    return

  def _predict_job (self, model_type: str, input, params:dict = None):
    result = None
    self.P(f"execution parameters: {params}")

    device = self.get_default_device()
    if (params and "device" in params and params['device'] is not None):
      device = self._get_device(params['device'])

    no_runs = 1
    if(params and "no_runs" in params and params['no_runs'] is not None):
      no_runs= self._get_device(params['no_runs'])

    if input:
      workername = None
      status = STATUS_CREATED 
      if self.__available :
        #check if current instance is available for processing
        workername = self.host
        status = STATUS_ASSIGNED
        self.__input = input

      # save job to database
      jobid = uuid.uuid4().hex
      try:
        self.postgres_insert_data(
            "jobs",
            uuid = jobid, 
            job_date = time.strftime("%Y-%m-%d %H:%M:%S"),
            model_type = model_type,
            device = device,
            no_runs = no_runs,
            status = status
        )
        self.P(f"Job saved: {jobid}")
      except Exception as exc:
        self.P("Error saving job to database: {}".format(exc))
        result = "Exception saving job to database"

      # save tasks to database
      if result is None:
        taskid = uuid.uuid4().hex
       
        if not self.__available :
        #if current insance is unavailable, save input to file
          task_content_path = self.cache_root+"/tasks/"+taskid+".bin"
          try:
            bytes_data = None
            os.makedirs(os.path.dirname(task_content_path), exist_ok=True)
            #transform input to bytes if necessary
            if isinstance(input, str):
              bytes_data = input.encode('utf-8')
            elif isinstance(input, bytes):
              bytes_data = input
            elif isinstance(input, List):
              bytes_data = json.dumps(input).encode('utf-8')
            with open(task_content_path, 'wb') as file:
              file.write(bytes_data)
              print(f"Data successfully written to {task_content_path}")
          except Exception as exc:
            self.P("Error saving job input: {}".format(exc))
            result = "Exception saving job input"
        
        if result is None:
          try:
            self.postgres_insert_data(
                "tasks",
                uuid = taskid, 
                jobid = jobid,
                workername = workername,
                status = status
            )
            result = jobid
            self.P(f"Task saved: {taskid}")
          except Exception as exc:
            self.P("Error saving task: {}".format(exc))
            result = "Exception saving processing task to database" 
    else:
      result = "Invalid input content"
    return  self.format_result(result, device) 

  def _predict(self, model_type: str, input, params:dict = None):
   avg_exec = 0
   exec_time =[]

   self.P(f"execution parameters: {params}")
   device = self.get_default_device()
   if (params and "device" in params and params['device'] is not None):
    device = self._get_device(params['device'])

   no_runs = 1
   if(params and "no_runs" in params and params['no_runs'] is not None):
     no_runs= self._get_device(params['no_runs'])

   if input:
    model = self.get_model(model_type, device)
    if model is None:
      prediction = "No model available"
    else:
      pipe = self.get_pipeline(model_type, device)
      if pipe is None:
        prediction = "No pipeline available"
      else:
        for i in range(no_runs):
          starttime=time.time_ns()
          prediction = pipe(input)
          exec_time.append((time.time_ns()-starttime)/1e+6)
          avg_exec += exec_time[-1]
        avg_exec = avg_exec/no_runs
        self.no_predictions += 1
        self._output_labels(model_type, prediction)
      self.save_state_to_db(result=prediction)
   else:
      prediction = "Invalid input content"
   return self.format_result(
     {
       "inference_result": prediction, 
       "inference_runs": no_runs,
       "inference_exec_time": exec_time,
       "inference_avg_exec_time": avg_exec
     }, 
     device
   )
  
  def predict_text(self, text: str, params: dict = None):
    self.P(f"Predict text: {text}")
    return self._predict_job('text', text , params)
  
  def predict_texts(self, texts: List[str], params: dict = None):
    self.P(f"Predict texts: {texts}")
    return self._predict_job('text', texts, params)
      
  def predict_image(self, image_data: bytes, params: dict = None):
    #image = Image.open(io.BytesIO(image_data))
    self.P(f"Predict image with size: {len(image_data)}")
    return self._predict_job('image', image, params)
  
  def predict_json(self, data: dict, params: dict = None):
    model = self.get_model('json')
    if model is None:
      prediction = "No model available"
    else:
      prediction = "Predict with struct model `{}` on data {}".format(model, data)
      self.no_predictions += 1
    self.save_state_to_db(result=prediction)
    return self.format_result(prediction)
  
  def get_predict_counts(self):
    result = self.postgres_get_count("predicts")
    return result
  
  def get_health(self):
    n_predictions = 5
    result = {
      "redis": self.redis_alive,
      "postgres" : self.postgres_alive,
      "lifetime_predictions": self.get_predict_counts(),
      "session_predictions": self.no_predictions,
      f"last_{n_predictions}_predictions" : self.postgres_select_data_ordered("predicts", "predict_date", "desc", n_predictions),
    }
    return self.format_result(result)

  