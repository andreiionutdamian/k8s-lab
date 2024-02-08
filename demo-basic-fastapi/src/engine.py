import os
import redis

from uuid import uuid4
from datetime import datetime

from app_utils import safe_jsonify, get_packages
from mixins.postgres_mixin import _PostgresMixin
from mixins.redis_mixin import _RedisMixin
from mixins.monitor_mixin import _MonitorMixin

__VER__ = '0.4.8'


class AppPaths:
  PATH_ROOT = {"PATH": "/", "FUNC": "root"}
  PATH_STAT = {"PATH": "/stats", "FUNC": "stats"  }

class AppHandler(
    _PostgresMixin, 
    _RedisMixin,
    _MonitorMixin,
  ):
  def __init__(self):
    self.log = None
    self.debug = os.environ.get("DEBUG", "0") in ['1', 'true', 'True', 'yes', 'Yes', 'y', 'Y', 'TRUE', 'YES']
    return
    
  def P(self, s, **kwargs):
    if vars(self).get('log') is not None :
      self.log.P(s, **kwargs)
    else:
      str_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      print('[APH][{}]'.format(str_date) + s, flush=True, **kwargs)
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
    self.__avail_paths = [v['PATH'] for k, v in vars(AppPaths).items() if k.startswith("PATH_")]
    self.__path_to_func = {v['PATH']: v['FUNC'] for k, v in vars(AppPaths).items() if k.startswith("PATH_")}
    self.__check_handlers()
    self.str_local_id = "test_" + str(uuid4())[:5]
    self.__local_count = 0
    self._has_redis = False
    self._has_postgres = False
    self.hostname = os.environ.get("HOSTNAME", "unknown")    
    self.P("Initializing {} v{} ID: {}, HOSTNAME: {}...".format(
      self.__class__.__name__, __VER__,
      self.str_local_id, self.hostname
    ))
    self.__packs = get_packages()
    self.P("Packages:\n{}".format("\n".join(self.__packs)))
    dct_env = dict(os.environ)
    if self.debug:
      self.P("Environement:\n{}".format(safe_jsonify(dct_env, indent=2)))
    self._maybe_setup_redis()
    self._maybe_setup_postgres()
    
    self.init_monitor()
    return
  
  def shutdown(self):
    self.P("Shutting down {}...".format(self.__class__.__name__))
    self.stop_monitor()
    self.P("Shutdown complete.")
    return
  
  
  def _process_data(self, param=None, **kwargs):
    self.__local_count += 1
    if self._has_redis:
      self.redis_inc("cluster_count")
      self.redis_sethash("data", self.str_local_id, self.__local_count)
    if self._has_postgres:
      str_data = "Data from {}:{}".format(self.str_local_id, self.__local_count)
      self.postgres_insert_data("requests", hostname=self.hostname, data=str_data)
    return
  
  def get_cluster_count(self):
    if self._has_redis:
      return self.redis_get("cluster_count")
    return 0

  
  def _pack_result(self, message, path=None, parameter=None):
    return {
      "result": message,
      "path": path,
      "parameter": parameter,
      "redis": self._has_redis,
      "postgres" : self._has_postgres,
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
    msg = "Handler '{}', Local/Global: {}/{}, HOSTNAME: '{}', ID: '{}'".format(
      kwargs['path'], self.__local_count, self.get_cluster_count(),
      self.hostname, self.str_local_id
    )    
    return msg
  
  def _handle_stats(self, **kwargs):
    dct_result = {
      'info' : "Handler '{}', Worker HOSTNAME: '{}', ID: '{}'".format(
        kwargs['path'], self.hostname, self.str_local_id
      ),
      'local_requests' : self.__local_count,
      'recent_requests' : self.redis_get("cluster_count"),
      'recent_stats' : self.redis_gethash("data"),
      'db_requests' : self.postgres_get_count("requests"),
      'db_stats' : self.postgres_select_counts("requests", "hostname"),     
    }    
    return dct_result
  
  
  def __handle_generic(self, path, parameter=None, **kwargs):
    msg = "Generic handler '{}', Param='{}', Local/Global: {}/{}, HOSTNAME: '{}', ID: '{}'".format(
      path, parameter, self.__local_count, self.get_cluster_count(),
      self.hostname, self.str_local_id
    )  
    return msg


if __name__ == '__main__':
  eng = AppHandler()
  print(eng.handle_request(AppPaths.PATH_ROOT))
  print(eng.handle_request(AppPaths.PATH_STAT))