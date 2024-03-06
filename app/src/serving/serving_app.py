from mixins.base_mixin import _BaseMixin
from mixins.postgres_mixin import _PostgresMixin
from mixins.redis_mixin import _RedisMixin
from mixins.kube_mixin import _KubeMixin

class ServingApp(
  _PostgresMixin,
  _RedisMixin,
  _KubeMixin,
  _BaseMixin,
  ):
  
  def __init__(self, **kwargs):
    super(ServingApp, self).__init__()

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
  
  def __get_k8s_status(self):
    """
    This function uses kube_mixin to get some status info from the k8s cluster
    """
    return self.get_namespace_info()
  
  def appmon_callback(self):
    super(ServingApp, self).appmon_callback()
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
  
   
  
  def get_health(self):
    result = {
      "redis": self.redis_alive,
      "postgres" : self.postgres_alive,
      "session_model_updates" : self.nr_updates,
      "lifetime_model_updates" : self.get_model_update_counts(),      
      "k8s_status" : self.__get_k8s_status(),
    }
    return result