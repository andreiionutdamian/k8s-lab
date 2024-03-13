import os

from datetime import datetime

from mixins.base_mixin import _BaseMixin
from mixins.postgres_mixin import _PostgresMixin
from mixins.redis_mixin import _RedisMixin
from mixins.kube_mixin import _KubeMixin

class MonitorApp(
  _PostgresMixin,
  _RedisMixin,
  _KubeMixin,
  _BaseMixin,
  ):
  
  def __init__(self, **kwargs):
    super(MonitorApp, self).__init__()
    self.log = None
    self.nr_updates = 0
    self.__initialized = False
    return  
  
  def __get_k8s_status(self):
    """
    This function uses kube_mixin to get some status info from the k8s cluster
    """
    return self.get_namespace_info()
  
  
  def setup(self):
    super(MonitorApp, self).setup()
    # now maybe add some custom code to initial setup
    return
  
  def appmon_callback(self):
    super(MonitorApp, self).appmon_callback()
    # now maybe add some custom code for initializations and configurations
    self.maybe_init_models()
    return
  
    
  def postgres_get_tables(self):
    tables ={
      "models" : "id SERIAL PRIMARY KEY, model_date varchar(50), model_type varchar(100), model_name varchar(200)"
    }
    return tables
  
  
  def save_model_update_to_db(self, model_type:str, model_name: str):  
    # save result to Postgres
    # TODO: is this safe for multi-worker setup?
    model_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self.postgres_insert_data(
      "models", 
      model_type=model_type, model_name=model_name, model_date=model_date
    )
    return
  
  
  def set_model(self, model_type: str, model: str):
    result = self.redis_sethash("models", model_type, model)
    msg = f"Model <{model_type}:{model}> set." if result else "Failed to set model"
    if result:
      self.save_model_update_to_db(model_type, model)
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
      "k8s_status" : self.__get_k8s_status(),       
    }
    return result
  
  def maybe_init_models(self):
    """
    This method will try to initialize Redis models from Postgres db:
      - run only if not __initialized
      - run the select from Postgres
      - if the select return None then we DO NOT have a active connection and return
      - else:
        - get the newest model for each model type     
        - push the models to Redis
        - set __initialized to True
    """
    if not self.__initialized:
      self.P("Loading models....")
      # get db models count if available
      db_count = self.postgres_get_count("models")
      if db_count is not None and db_count > 0 :
        # get a count grouped by model_type to get the list of types
        model_types = self.postgres_group_count("models","model_type")
        self.P(f"Model types: {model_types}")
        #iterate model types
        for model_type in model_types:
          models = self.postgres_select_data("models", model_type=model_type[0])
          latest = None
          # iterate models and get latest
          for model in models:
            model_date = model[1]
            model_name = model[3]
            if latest is None:
              latest = model
            else:
              if datetime.strptime(model_date,"%Y-%m-%d %H:%M") > datetime.strptime(latest[1],"%Y-%m-%d %H:%M") :
                latest = model
              #endif
            #endif
          #endfor
          self.redis_set(model_type[0], latest[3])
          self.P(f"Cache update: {model_type[0]} - {latest[3]}")
        #endfor
        self.__initialized = True
      #endif
    #endif
    return  
  