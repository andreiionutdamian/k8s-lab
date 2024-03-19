import os

from datetime import datetime

from mixins.base_mixin import _BaseMixin
from mixins.postgres_mixin import _PostgresMixin
from mixins.redis_mixin import _RedisMixin
from mixins.llm_mixin import _LlmMixin

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
    return
  
  def setup(self):
    super(ServingApp, self).setup()    
    # setup serving
    self.models = {
      'text' : None,
      'json' : None,
      'image' : None,
    }

    self.pipes = {
      'text' : None,
      'json' : None,
      'image' : None,
    }
    return
  
  
  def appmon_callback(self):
    super(ServingApp, self).appmon_callback()
    return
  
  def postgres_get_tables(self):
    tables ={
      "predicts" : "id SERIAL PRIMARY KEY, predict_date varchar(50), result varchar(255)"
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
  
  def maybe_setup_model(self, model_type:str):
    # get models from Redis if available
    redis_model = self.redis_hget("models", model_type)
    if redis_model is not None  and redis_model is not "":
      self.models[model_type] = redis_model
      if os.path.exists(self.cache_root+"/"+redis_model):
        self.pipes[model_type] = self.load_model(model_type, redis_model, True)
      else:
        raise ValueError("Model not initialized") 
      # now mark as "seen"
      # self.redis_sethash("models", model_type, "")
    return
  
  def save_state_to_db(self, result):
    # TODO: is this safe for multi worker? - YES
    to_save = str(result)[:255]
    predict_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # save result to Postgres
    self.postgres_insert_data("predicts", result=to_save, predict_date=predict_date)
    return
  
  def get_model(self, model_type: str):
    # get model from Redis
    redis_model = self.redis_hget("models", model_type)
    model = self.models[model_type]
    if redis_model is not None and ( model is None or model != redis_model) :
      try:
        self.maybe_setup_model(model_type) # only missing models should be loaded not all
        model = self.models[model_type]
      except Exception as exc:
        self.P("Error loading model: {}".format(exc))
    return model
  
  def get_pipeline(self, model_type: str):
    pipe = self.pipes[model_type]
    if pipe is None:
      try:
        self.maybe_setup_model(model_type) # only missing models should be loaded not all
        pipe = self.pipes[model_type]
      except Exception as exc:
        self.P("Error loading model: {}".format(exc))
    return pipe
  
  def predict_text(self, text: str):
    model = self.get_model('text')
    if model is None:
      prediction = "No model available"
    else:
      pipe = self.get_pipeline('text')
      # prediction = "Predict with text-input model `{}` on text '{}'".format(model, text)
      if pipe is None:
        prediction = "No pipeline available"
      else:
        prediction = pipe(text)
        self.no_predictions += 1
    self.save_state_to_db(result=prediction)
    return self.format_result(prediction)
  
  
  def predict_json(self, data: dict):
    model = self.get_model('json')
    if model is None:
      prediction = "No model available"
    else:
      prediction = "Predict with struct model `{}` on data {}".format(model, data)
      self.no_predictions += 1
    self.save_state_to_db(result=prediction)
    return self.format_result(prediction)
  
  
  def predict_image(self, image: bytes):
    model = self.get_model('image')
    if model is None:
      prediction = "No model available"
    else:
      prediction = "Predict with image model `{}` on image size {}".format(model, len(image))
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

  