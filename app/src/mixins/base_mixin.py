import os

from app_utils import safe_jsonify, get_packages

from threading import Thread, Lock
from time import sleep
from datetime import datetime
from uuid import uuid4
from version import __VER__

class _BaseMixin(object):
  def __init__(self):
    super(_BaseMixin, self).__init__()
    
    self.__done = False
    self.__started = False
    self._packs = None
    self.__print_lock = Lock()
    self.__resolution = os.environ.get("MONITOR_RESOLUTION", 0.25)
    self.P("Base functions initialized.")
    return
  
  
  @property
  def is_started(self):
    return self.__started 


  def P(self, s, **kwargs):
    if vars(self).get('log') is not None :
      self.log.P(s, **kwargs)
    else:
      self.__print_lock.acquire()
      str_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      prefix = self.__class__.__name__[:4].upper()
      print('[{}][{}] '.format(prefix, str_date) + s, flush=True, **kwargs)
      self.__print_lock.release() 
    return  


  def setup(self):
    self.str_local_id = "test_" + str(uuid4())[:5]
    self.hostname = os.environ.get("HOSTNAME", "unknown")    
    self.P("Initializing {} <{}> v{} on {}".format(
      self.__class__.__name__, __VER__,
      self.str_local_id, self.hostname
    ))
    
    if False: # in main.py already True ?
      self._packs = get_packages()
      self.P("Packages:\n{}".format("\n".join(self._packs)))
      
    if self.debug:
      dct_env = dict(os.environ)
      self.P("Environment:\n{}".format(safe_jsonify(dct_env, indent=2)))
      
    self.redis_maybe_connect()
    self.postgres_maybe_connect()

    self.start_monitor()
    return


  def shutdown(self):
    self.P("Shutting down {}...".format(self.__class__.__name__))
    self.stop_monitor()
    self.P("Shutdown complete.")
    return

  
  def config_appmon(self):
    # Override this method to configure the monitor
    return  
  
  
  def stop_appmon(self):
    self.__done = True
    return
  
  
  def start_appmon(self):
    self.config_monitor()
    self.__done = False
    self.appmon_thread = Thread(target=self.appmon_loop, daemon=True)
    self.appmon_thread.start()
    return  


  def appmon_callback(self):
    methods = [m for m in dir(self) if m.endswith("_maybe_connect")]
    for method in methods:
      self.P(f"*** Running monitor callback: {method}... ***")
      func = getattr(self, method)
      func()
    return
  
  
  def appmon_loop(self):  
    self.P("Initializing monitor loop with resolution: {}...".format(self.__resolution))
    self.__started = True
    while not self.__done:
      sleep(1 / self.__resolution)
      self.appmon_callback()
    return
    
    
    