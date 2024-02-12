import os
import redis

from uuid import uuid4
from datetime import datetime


from app_utils import safe_jsonify, get_packages
from mixins.postgres_mixin import _PostgresMixin
from mixins.redis_mixin import _RedisMixin

from mixins.base_mixin import _BaseMixin

from version import __VER__

class AppPaths:
  PATH_ROOT = {"PATH": "/", "FUNC": "root"}
  PATH_STAT = {"PATH": "/stats", "FUNC": "stats"  }

class AppHandler(
    _PostgresMixin, 
    _RedisMixin,
    _BaseMixin,
  ):
  def __init__(self, *args, **kwargs):
    super(AppHandler, self).__init__(*args, **kwargs)
    self.log = None
    self.debug = os.environ.get("DEBUG", "0") in ['1', 'true', 'True', 'yes', 'Yes', 'y', 'Y', 'TRUE', 'YES']
    return
 
  
  def __check_handlers(self):
    requested_funcs = ["_handle_" + x for x in self.__path_to_func.values()]
    for func in requested_funcs:
      if not hasattr(self, func):
        msg = "Handler function '{}' not found in class '{}'. Available handlers: {}, Paths: {}".format(
          func, self.__class__.__name__,
          [x for x in dir(self) if x.startswith("_handle_")],
          {k:v for k, v in vars(AppPaths).items() if k.startswith("PATH_")},
        )
        raise Exception(msg)
      #end if not hasattr
    #end check for handlers
    return
  
  
  def setup(self):
    super(AppHandler, self).setup()

    self.__avail_paths = [v['PATH'] for k, v in vars(AppPaths).items() if k.startswith("PATH_")]
    self.__path_to_func = {v['PATH']: v['FUNC'] for k, v in vars(AppPaths).items() if k.startswith("PATH_")}
    self.__check_handlers()
    self.__local_count = 0    
    return
  
  def monitor_callback(self):
    super(AppHandler, self).monitor_callback()
    return
    
  
  def _process_data(self, param=None, **kwargs):
    self.__local_count += 1
    if self.redis_alive:
      self.redis_inc("cluster_count")
      self.redis_sethash("data", self.hostname, self.__local_count)
    if self.postgres_alive:
      str_data = "Data from {}:{}".format(self.str_local_id, self.__local_count)
      self.postgres_insert_data("requests", hostname=self.hostname, data=str_data)
    return
  
  
  def postgres_get_tables(self):
    tables ={
      "requests" : "id SERIAL PRIMARY KEY, hostname varchar(200), data varchar(255)"
    }
    return tables
  
  
  def get_redis_count(self):
    return self.redis_get("cluster_count")
  
  
  def get_redis_stats(self):
    dct_res = self.redis_gethash("data")
    dct_res["total"] = sum(dct_res.values())
    result = dct_res
    return result
  
  
  def get_db_requests(self):
    result = 0
    if self.postgres_alive:
      result = self.postgres_get_count("requests")
    return result

  def get_db_stats(self):
    result = {}
    if self.postgres_alive:
      rows = self.postgres_group_count("requests", "hostname")
      dct_res = {k:v for k, v in rows}
      dct_res["total"] = sum(dct_res.values())
      result = dct_res
    return result
  
  def _pack_result(self, message, path=None, parameter=None):
    return {
      "result": message,
      "path": path,
      "parameter": parameter,
      "redis": self.redis_alive,
      "postgres" : self.postgres_alive,
    }  
  
   
  
  def handle_request(self, path, parameter=None):
    self._process_data(param=parameter)
    if path in self.__avail_paths:
      func_name = '_handle_' + self.__path_to_func[path]
      msg = getattr(self, func_name)(path=path)
    else:
      msg = self.__handle_generic(path)
    result = self._pack_result(msg, path=path, parameter=parameter)
    return result
    

  def _handle_root(self, **kwargs):
    msg = "'{}', Local/Global: {}/{}, HOSTNAME: '{}', ID: '{}'".format(
      kwargs['path'], self.__local_count, self.get_redis_count(),
      self.hostname, self.str_local_id
    )    
    return msg
  
  def _handle_stats(self, **kwargs):
    dct_result = {
      'info' : "'{}', HOSTNAME: '{}', ID: '{}'".format(
        kwargs['path'], self.hostname, self.str_local_id
      ),
      'local_requests' : self.__local_count,
      'recent_requests' : self.get_redis_count(),
      'recent_stats' : self.get_redis_stats(),
      'db_requests' : self.get_db_requests(),
      'db_stats' : self.get_db_stats(),     
    }    
    return dct_result
  
  
  def __handle_generic(self, path, **kwargs):
    msg = "Generic '{}', Local/Global: {}/{}, HOSTNAME: '{}', ID: '{}'".format(
      path, self.__local_count, self.get_redis_count(),
      self.hostname, self.str_local_id
    )  
    return msg


if __name__ == '__main__':
  eng = AppHandler()
  print(eng.handle_request(AppPaths.PATH_ROOT))
  print(eng.handle_request(AppPaths.PATH_STAT))