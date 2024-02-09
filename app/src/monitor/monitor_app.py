from mixins.base_mixin import _BaseMixin
from mixins.postgres_mixin import _PostgresMixin
from mixins.redis_mixin import _RedisMixin

class MonitorApp(
  _BaseMixin,
  _PostgresMixin,
  _RedisMixin,
  ):
  
  def __init__(self, **kwargs):
    super(MonitorApp, self).__init__(**kwargs)
    self.log = None
    return  
  
  def setup(self):
    super(MonitorApp, self).setup()
    return
    
  def postgres_maybe_create_tables(self):
    if self._has_postgres:
      with self.__pg.cursor() as cur:
        # cur.execute("CREATE TABLE IF NOT EXISTS requests (id SERIAL PRIMARY KEY, hostname varchar(200), data varchar(255));")
        self.__pg.commit()        
    return
  
  
  def set_model(self, model_type: str, model: str):
    result = self.redis_sethash("models", model_type, model)
    msg = f"Model <{model_type}:{model}> set." if result else "Failed to set model"
    return msg
  
  def get_health(self):
    result = {
      "redis": self.redis_alive,
      "postgres" : self.postgres_alive,
    }
    return result
  
  