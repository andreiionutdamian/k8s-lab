from mixins.base_mixin import _BaseMixin
from mixins.postgres_mixin import _PostgresMixin
from mixins.redis_mixin import _RedisMixin

class ServingApp(
  _BaseMixin,
  _PostgresMixin,
  _RedisMixin,
  ):
  
  def __init__(self, **kwargs):
    super(ServingApp, self).__init__(**kwargs)

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
    return
  
  def monitor_callback(self):
    super(ServingApp, self).monitor_callback()
    return
  
  def postgres_get_tables(self):
    tables ={
      "predicts" : "id SERIAL PRIMARY KEY, hostname varchar(200), result varchar(255)"
    }
    return tables

  
  def __load_model(self, model_type: str, model_name: str):
    # load models 
    return
  
  
  def maybe_setup_models(self):
    # get models from Redis if available
    redis_models = self.redis_gethash("models")
    if len(redis_models) > 0:
      for k in self.models:
        redis_model = redis_models.get(k, None)
        if redis_model is not None:
          self.models[k] = redis_model
          self.__load_model(k, redis_model)
          # now mark as "seen"
          self.redis_sethash("models", k, None)
    return
  
  def save_state_to_db(self, result):
    to_save = str(result)[:255]
    # save result to Postgres
    self.postgres_insert_data("predicts", result=to_save)
    return
  
  def get_model(self, model_type: str):
    # get model from Redis
    model = self.models[model_type]
    if model is None:
      self.setup_models()
      model = self.models[model_type]
    return model
  
  def predict_text(self, text: str):
    model = self.get_model('text')
    if model is None:
      prediction = "No model available"
    else:
      prediction = "Predict with text-input model: '{}' on text {}".format(model, text)
    self.save_state_to_db(result=prediction)
    return prediction
  
  
  def predict_json(self, data: dict):
    model = self.get_model('json')
    if model is None:
      prediction = "No model available"
    else:
      prediction = "Predict with struct model: '{}' on data {}".format(model, data)
    self.save_state_to_db(result=prediction)
    return prediction
  
  
  def predict_image(self, image: bytes):
    model = self.get_model('image')
    if model is None:
      prediction = "No model available"
    else:
      prediction = "Predict with image model: '{}' on image {}".format(model, len(image))
    self.save_state_to_db(result=prediction)
    return prediction