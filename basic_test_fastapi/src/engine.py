import os
import redis
import json
from uuid import uuid4
from datetime import datetime

from app_utils import safe_jsonify

__VER__ = '0.2.5'


class AppPaths:
  PATH_ROOT = {"PATH": "/", "FUNC": "root"}
  PATH_STAT = {"PATH": "/stat", "FUNC": "stat"  }

class AppHandler:
  def __init__(self):
    self.log = None
    self.__setup()
    return
  
  def P(self, s, **kwargs):
    if vars(self).get('log') is not None :
      self.log.P(s, **kwargs)
    else:
      str_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      print('[APH][{}]'.format(str_date) + s, flush=True, **kwargs)
    return
  
  def __setup(self):
    self.__avail_paths = [v['PATH'] for k, v in vars(AppPaths).items() if k.startswith("PATH_")]
    self.__path_to_func = {v['PATH']: v['FUNC'] for k, v in vars(AppPaths).items() if k.startswith("PATH_")}
    self.str_local_id = "test_" + str(uuid4())[:5]
    self.__local_count = 0
    self.__has_redis = False
    self.hostname = os.environ.get("HOSTNAME", "unknown")    
    self.P("Initializing {} v{} ID: {}, HOSTNAME: {}...".format(
      self.__class__.__name__, __VER__,
      self.str_local_id, self.hostname
    ))
    dct_env = dict(os.environ)
    self.P("Environement:\n{}".format(safe_jsonify(dct_env, indent=2)))
    self.__maybe_setup_redis()
    return
    
  def __maybe_setup_redis(self):
    dct_redis = {k : v for k, v in os.environ.items() if k.startswith("REDIS_")}
    if len(dct_redis) > 0:
      if "REDIS_MASTER_SERVICE_HOST" in dct_redis:
        # this is a redis master/slave setup
        self.P("Setting up Redis with master/slave configuration:\n{}".format(safe_jsonify(dct_redis)))
        redis_host = dct_redis.get("REDIS_MASTER_SERVICE_HOST")
        redis_port = dct_redis.get("REDIS_MASTER_SERVICE_PORT")
        redis_password = dct_redis.get("REDIS_PASSWORD")
        # redis_master_port = dct_redis.get("REDIS_MASTER_PORT")
      else:
        self.P("Setting up simple Redis with configuration:\n{}".format(safe_jsonify(dct_redis)))
        redis_host = dct_redis.get("REDIS_SERVICE_HOST")
        redis_port = dct_redis.get("REDIS_SERVICE_PORT", 6379)
        redis_password = dct_redis.get("REDIS_PASSWORD", None)
      hidden_password = redis_password[:2] + "*" * (len(redis_password) - 4) + redis_password[-2:] if redis_password is not None else None
      self.P("Connecting to Redis at {}:{} with password: {}".format(
        redis_host, redis_port, hidden_password
      ))
      self.__redis = redis.Redis(
        host=redis_host, port=redis_port, 
        password=redis_password, 
        decode_responses=True,
      )
      self.__has_redis = True
      self.P("Connected to Redis at {}:{}".format(redis_host, redis_port))
      self.P("Redis info:\n {}".format(safe_jsonify(self.__redis.info())))
      return
    self.__has_redis = False
    return
    
  def _pack_result(self, message):
    return {"result": message}

  def _inc_cluster_count(self):
    if self.__has_redis:
      self.__redis.incr("cluster_count")
    return
  
  def get_cluster_count(self):
    result = self.__local_count
    if self.__has_redis:
      # get the value from redis
      result = self.__redis.get("cluster_count")
    return result
  
  
  def get_data(self):
    if not self.__has_redis:
      return {}
    return self.__redis.hgetall("data")
  
  
  def process_data(self):
    self.__local_count += 1
    if self.__has_redis:
      self._inc_cluster_count()
      self.__redis.hset("data", self.str_local_id, self.__local_count)
    return
  
  
  def handle_request(self, path):
    self.process_data()
    if path in self.__avail_paths:
      func_name = '_handle_' + self.__path_to_func[path]
      msg = getattr(self, func_name)()
    else:
      msg = self.__handle_generic(path)
    result = self._pack_result(msg)
    return result
    

  def _handle_root(self):
    msg = "Handler '{}', Local/Global: {}/{}, HOSTNAME: '{}', ID: '{}'".format(
      AppPaths.PATH_ROOT, self.__local_count, self.get_cluster_count(),
      self.hostname, self.str_local_id
    )    
    return msg
  
  def _handle_stat(self):
    dct_result = {
      'info' : "Handler '{}', Worker HOSTNAME: '{}', ID: '{}'".format(
        AppPaths.PATH_STAT, self.hostname, self.str_local_id
      ),
      'local_count' : self.__local_count,
      'cluster_count' : self.get_cluster_count(),
      'cluster_data' : self.get_data(),
    }    
    return dct_result
  
  
  def __handle_generic(self, path):
    msg = "Generic handler '{}', Local/Global: {}/{}, HOSTNAME: '{}', ID: '{}'".format(
      path, self.__local_count, self.get_cluster_count(),
      self.hostname, self.str_local_id
    )  
    return msg


if __name__ == '__main__':
  eng = AppHandler()
  print(eng.handle_request(AppPaths.PATH_ROOT))
  print(eng.handle_request(AppPaths.PATH_STAT))