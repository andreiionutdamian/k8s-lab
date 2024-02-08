import os
import redis
import psycopg2

from uuid import uuid4
from datetime import datetime

from app_utils import safe_jsonify, get_packages

__VER__ = '0.3.4'


class AppPaths:
  PATH_ROOT = {"PATH": "/", "FUNC": "root"}
  PATH_STAT = {"PATH": "/stats", "FUNC": "stats"  }

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
  
  
  def __setup(self):
    self.__avail_paths = [v['PATH'] for k, v in vars(AppPaths).items() if k.startswith("PATH_")]
    self.__path_to_func = {v['PATH']: v['FUNC'] for k, v in vars(AppPaths).items() if k.startswith("PATH_")}
    self.__check_handlers()
    self.str_local_id = "test_" + str(uuid4())[:5]
    self.__local_count = 0
    self.__has_redis = False
    self.__has_postgres = False
    self.hostname = os.environ.get("HOSTNAME", "unknown")    
    self.P("Initializing {} v{} ID: {}, HOSTNAME: {}...".format(
      self.__class__.__name__, __VER__,
      self.str_local_id, self.hostname
    ))
    self.__packs = get_packages()
    self.P("Packages:\n{}".format("\n".join(self.__packs)))
    dct_env = dict(os.environ)
    self.P("Environement:\n{}".format(safe_jsonify(dct_env, indent=2)))
    self.__maybe_setup_redis()
    self.__maybe_setup_postgres()
    return
  
  
  ### Redis
  
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
  
  
  def __get_redis_data(self):
    if not self.__has_redis:
      return {}
    return self.__redis.hgetall("data")
    
  def __maybe_setup_redis(self):
    self.__has_redis = False
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
  
  
  # PostgreSQL
    
  def __maybe_create_tables(self):
    if self.__has_postgres:
      with self.__pg.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS requests (id SERIAL PRIMARY KEY, hostname varchar(200), data varchar(255));")
        self.__pg.commit()
        
    return
  
  def __insert_data(self, data : str):
    if self.__has_postgres:
      with self.__pg.cursor() as cur:
        host : str = self.hostname
        cur.execute("INSERT INTO requests (hostname, data) VALUES (%s, %s);", (host, data,))
        self.__pg.commit()
    return
  
  
  def __get_db_request_count(self):
    result = None
    if self.__has_postgres:
      with self.__pg.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM requests;")
        rows = cur.fetchall()
        result = rows
    return result
  
  
  def __get_db_stats(self):
    result = None
    if self.__has_postgres:
      with self.__pg.cursor() as cur:
        cur.execute("SELECT hostname, COUNT(*) FROM requests GROUP BY hostname;")
        rows = cur.fetchall()
        result = rows
    return result
    
  
  def __maybe_setup_postgres(self):
    dct_pg = {k : v for k, v in os.environ.items() if k.startswith("POSTGRES_")}
    self.__has_postgres = False
    if len(dct_pg) > 0:
      self.P("Setting up Postgres with configuration:\n{}".format(safe_jsonify(dct_pg)))
      postgres_host = dct_pg.get("POSTGRES_SERVICE_HOST")
      postgres_port = dct_pg.get("POSTGRES_SERVICE_PORT", 5432)
      postgres_user = dct_pg.get("POSTGRES_USER")
      postgres_password = dct_pg.get("POSTGRES_PASSWORD")
      self.P("Connecting to Postgres at {}:{} with user: {}".format(
        postgres_host, postgres_port, postgres_user
      ))
      self.__pg = psycopg2.connect(
        host=postgres_host, port=postgres_port,
        user=postgres_user, password=postgres_password
      )
      pg_server_info = self.__pg.get_dsn_parameters()
      self.P("Connected to Postgres at {}:{} with user: {} to database: {}".format(
        pg_server_info['host'], pg_server_info['port'], 
        pg_server_info['user'], pg_server_info['dbname'],
      ))
      self.__maybe_create_tables()
      # now we get the tables from the database
      with self.__pg.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        rows = cur.fetchall()
        self.P("Tables in the database: {}".format(rows))
      self.__has_postgres = True
    return
    

  
  
  def __process_redis_data(self):
    self.__local_count += 1
    if self.__has_redis:
      self._inc_cluster_count()
      self.__redis.hset("data", self.str_local_id, self.__local_count)
    return
  
  
  def __process_postgres_data(self):
    if self.__has_postgres:
      self.__insert_data("Data from {}:{}".format(self.str_local_id, self.__local_count))
    return
  
  def _pack_result(self, message, path=None, parameter=None):
    return {
      "result": message,
      "path": path,
      "parameter": parameter,
      "redis": self.__has_redis,
      "postgres" : self.__has_postgres,
    }  
  
  
  def _process_data(self, param=None):
    self.__process_redis_data()
    self.__process_postgres_data()
    return
  
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
      'recent_requests' : self.get_cluster_count(),
      'recent_stats' : self.__get_redis_data(),
      'db_requests' : self.__get_db_request_count(),
      'db_stats' : self.__get_db_stats(),      
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