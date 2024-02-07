import os
import redis
import json
from uuid import uuid4

__VER__ = '0.1.0'

class AppPaths:
  PATH_ROOT = "/"
  PATH_STAT = "/stats"

class AppHandler:
  def __init__(self):
    self.log = None
    self.__setup()
    return
  
  def P(self, s, **kwargs):
    if vars(self).get('log') is not None :
      self.log.P(s, **kwargs)
    else:
      print('[APH]' + s, flush=True, **kwargs)
    return
  
  def __setup(self):
    self.str_local_id = "test_" + str(uuid4())[:5]
    self.__local_count = 0
    self.__has_redis = False
    self.hostname = os.environ.get("HOSTNAME", "unknown")    
    self.P("Initializing {} v{}  with ID: {}, HOSTNAME: {}...".format(
      self.__class__.__name__, __VER__,
      self.str_local_id, self.hostname
    ))
    dct_env = dict(os.environ)
    self.P("Environement:\n{}".format(json.dumps(dct_env, indent=2)))
    self.__maybe_setup_redis()
    return
    
  def __maybe_setup_redis(self):
    self.__has_redis = False
    return
    
  def _pack_result(self, message):
    return {"result": message}
  
  def get_cluster_count(self):
    result = self.__local_count
    if self.__has_redis:
      # get the value from redis
      pass
    return result
  
  
  def handle_request(self, path):
    self.__local_count += 1
    if path == AppPaths.PATH_ROOT:
      msg = self.handle_root()
    elif path == AppPaths.PATH_STAT:
      msg = self.handle_stat()
    else:
      msg = self.handle_generic(path)
    result = self._pack_result(msg)
    return result
    

  def handle_root(self):
    msg = "Handler '{}', Local/Global: {}/{}, HOSTNAME: '{}', ID: '{}'".format(
      AppPaths.PATH_ROOT, self.__local_count, self.get_cluster_count(),
      self.hostname, self.str_local_id
    )    
    return msg
  
  def handle_stat(self):
    dct_result = {
      'info' : "Handler '{}', Worker HOSTNAME: '{}', ID: '{}'".format(
        AppPaths.PATH_STAT, self.hostname, self.str_local_id
      ),
      'local_count' : self.__local_count,
      'cluster_count' : self.get_cluster_count(),
    }    
    return dct_result
  
  
  def handle_generic(self, path):
    msg = "Generic handler '{}', Local/Global: {}/{}, HOSTNAME: '{}', ID: '{}'".format(
      path, self.__local_count, self.get_cluster_count(),
      self.hostname, self.str_local_id
    )  
    return msg


if __name__ == '__main__':
  eng = AppHandler()
  print(eng.handle_request(AppPaths.PATH_ROOT))
  print(eng.handle_request(AppPaths.PATH_STAT))