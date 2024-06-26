import os
import json

from datetime import datetime

from mixins.base_mixin import _BaseMixin
from mixins.postgres_mixin import _PostgresMixin
from mixins.redis_mixin import _RedisMixin
from mixins.kube_mixin import _KubeMixin
from mixins.llm_mixin import _LlmMixin

class MonitorApp(
  _LlmMixin,
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
      "models" : "id SERIAL PRIMARY KEY, model_date varchar(50), model_type varchar(100), model_name varchar(200), dlabels json"
    }
    return tables
  
  
  def save_model_update_to_db(self, model_type:str, model_name: str, labels: dict):  
    # save result to Postgres
    # TODO: is this safe for multi-worker setup?
    model_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    self.postgres_insert_data(
      "models", 
      model_type=model_type, model_name=model_name, model_date=model_date, 
      dlabels=json.dumps(labels)
    )
    return
  
  def _update_cache(self, model_type:str, model_name : str, labels:dict = None):
    result = self.redis_sethash("models", model_type, model_name)
    if result:
      self.P(f"Cache update model: {model_type} - {model_name}")
    
    if labels is not None:
      result = self.redis_sethash("labels", model_name, json.dumps(labels))
      self.P(f"Cache update labels: {model_name} - {labels}")

    return result

  def set_model(self, model_type: str, model_name: str, labels: dict):
    result = None
    model = self.load_model(model_type, model_name)
    if model is not None:
      result = self._update_cache (model_type, model_name, labels)
      if result:
        self.save_model_update_to_db(model_type, model_name, labels)
        self.nr_updates += 1
      #endif
    #endif
    msg = f"Model {model_name} for type {model_type} set" if result else "Failed to set model"
    return self.format_result(msg)
  
  def update_monitor(self, app_module: dict):
    result = self.update_deployment(
      deployment_name="ai-app-mon",
      container_name="ai-app-mon-container",
      new_ver=app_module['new_ver'],
      check_ver=app_module['cur_ver']
    )
    return self.format_result(result)
  
  def update_serving(self, app_module: dict):
    result = self.update_statefulset(
      sset_name="ai-app-serve",
      container_name="ai-app-serve-container",
      new_ver=app_module['new_ver'],
      check_ver=app_module['cur_ver']
    )
    return self.format_result(result)
  
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
    return self.format_result(result)
  
  def get_latest_model(self, model_type: str):
    latest = None
    models = self.postgres_select_data("models", for_update=False, model_type=model_type)
    if models:
      # iterate models and get latest
      for model in models:
        model_date = model[1]
        model_name = model[3]
        if latest is None:
          latest = model
        else:
          if datetime.strptime(model_date,"%Y-%m-%d %H:%M:%S") > datetime.strptime(latest[1],"%Y-%m-%d %H:%M:%S") :
            latest = model
          #endif
        #endif
      #endfor
    #endif
    return latest
  
  def get_latest_model_top(self, model_type: str):
    latest = None
    models = self.postgres_select_data_ordered(
      table_name="models",for_update=False, 
      order_by="model_date", order="desc", 
      maxrows=1,  model_type=model_type
    )
    if models:
      latest = models[0]
    #endif
    return latest
  

  
  def maybe_init_models(self):
    """
    TODO refactor using two possible methods - iterative and with top rows
    """
    if not self.__initialized:
      self.P("Loading models....")
      # get db models count if availablecat 
      db_count = self.postgres_get_count("models")
      if db_count is not None and db_count > 0 :
        # get a count grouped by model_type to get the list of types
        model_types = self.postgres_group_count("models","model_type")
        self.P(f"Model types: {model_types}")
        #iterate model types
        for model_type in model_types:
          latest = self.get_latest_model_top(model_type[0])
          model = self.load_model(model_type[0], latest[3])
          model_exists = model is not None
          if model_exists:
            self._update_cache (
              model_type=model_type[0], 
              model_name=latest[3], 
              labels=latest[4]
          )
          #endif
        #endfor
        self.__initialized = True
      #endif
    #endif
    return  
  