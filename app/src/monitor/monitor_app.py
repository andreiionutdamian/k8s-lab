from datetime import datetime

from mixins.base_mixin import _BaseMixin
from mixins.postgres_mixin import _PostgresMixin
from mixins.redis_mixin import _RedisMixin

class MonitorApp(
  _PostgresMixin,
  _RedisMixin,

  _BaseMixin,
  ):
  
  def __init__(self, **kwargs):
    super(MonitorApp, self).__init__(**kwargs)
    self.log = None
    self.nr_updates = 0
    return  
  
  def setup(self):
    super(MonitorApp, self).setup()
    return
  
  def monitor_callback(self):
    super(MonitorApp, self).monitor_callback()
    return
  
    
  def postgres_get_tables(self):
    tables ={
      "models" : "id SERIAL PRIMARY KEY, model_name varchar(200), model_date varchar(250)"
    }
    return tables
  
  
  def save_model_update_to_db(self, data: str):
    # save result to Postgres
    model_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self.postgres_insert_data("models", model_name=data, model_date=model_date)
    return
  
  
  def set_model(self, model_type: str, model: str):
    result = self.redis_sethash("models", model_type, model)
    msg = f"Model <{model_type}:{model}> set." if result else "Failed to set model"
    if result:
      self.save_model_update_to_db(model)
      self.nr_updates += 1
    return msg
  
  def get_model_update_counts(self):
    result = self.postgres_get_count("models")
    return result
  
  def get_health(self):
    result = {
      "redis": self.redis_alive,
      "postgres" : self.postgres_alive,
      "session_model_updates" : self.nr_updates,
      "lifetime_model_updates" : self.get_model_update_counts(),      
    }
    return result
  
  