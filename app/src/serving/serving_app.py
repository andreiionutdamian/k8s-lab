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
  
  def maybe_setup_models(self):
    # get models from Redis if available
    return
  
  def save_state_to_db(self, result):
    to_save = str(result)
    # save result to Postgres
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
      prediction = "Predict with model: '{}' on text {}".format(model, text)
    return prediction
  
  
  def predict_json(self, data: dict):
    model = self.get_model('json')
    if model is None:
      prediction = "No model available"
    else:
      prediction = "Predict with model: '{}' on data {}".format(model, data)
    return prediction
  
  
  def predict_image(self, image: bytes):
    model = self.get_model('image')
    if model is None:
      prediction = "No model available"
    else:
      prediction = "Predict with model: '{}' on image {}".format(model, len(image))
    return prediction