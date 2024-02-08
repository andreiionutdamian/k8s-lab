import os
import redis
from app_utils import safe_jsonify

INFO_KEYS = [
  "redis_version",  
  "redis_mode",
  "connected_clients",
  "used_memory_human", 
  "pubsub_channels",
]
class _RedisMixin:
  def __init__(self, *args, **kwargs):
    self.__redis = None
    return
  
  
  def __get_redis_config(self):
    dct_redis = {k : v for k, v in os.environ.items() if k.startswith("REDIS_")}
    return dct_redis
  
    
  def _maybe_setup_redis(self):
    self._has_redis = False
    dct_redis = self.__get_redis_config()
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
      self._has_redis = True
      self.P("Connected to Redis at {}:{}".format(redis_host, redis_port))
      self.__redis_info = {
        k : v for k, v in self.__redis.info().items() 
        if k in INFO_KEYS
      } 
      self.P("Redis info:\n {}".format(safe_jsonify(self.__redis.info())))
    return
  
  
  def redis_inc(self, key : str, amount : int = 1):
    if self._has_redis:
      self.__redis.incr(key, amount)
    return
  
  
  def redis_set(self, key : str, value):
    if self._has_redis:
      self.__redis.set(key, value)
    return
  
  def redis_sethash(self, hashname : str, key : str, value):
    if self._has_redis:
      self.__redis.hset(hashname, key, value)
    return  
  
  def redis_get(self, key : str):
    result = None
    if self._has_redis:
      result = self.__redis.get(key)
    return result
  
  def redis_gethash(self, hashname : str):
    result = None
    if self._has_redis:
      result = self.__redis.hget(hashname)
    return result