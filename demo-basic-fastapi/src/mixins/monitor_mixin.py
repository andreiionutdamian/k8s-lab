import os

from threading import Thread
from time import sleep

class _MonitorMixin:
  def __init__(self, **kwargs):
    self.__done = False
    self.__started = False
    self.__resolution = os.environ.get("MONITOR_RESOLUTION", 0.25)
    return
  
  @property
  def is_started(self):
    return self.__started 
  
  def init_monitor(self):
    pass
  
  
  def stop_monitor(self):
    self.__done = True
    return
  
  
  def start_monitor(self):
    self.__done = False
    self.monitor_thread = Thread(target=self.monitor_loop, daemon=True)
    self.monitor_thread.start()
    return  
  
  
  def monitor_callback(self):
    raise NotImplementedError("monitor_callback() must be implemented by the subclass")
  
  
  def monitor_loop(self):  
    self.P("Initializing monitor loop with resolution: {}...".format(self.__resolution))
    self.__started = True
    while not self.__done:
      sleep(1 / self.__resolution)
      self.monitor_callback()
    return
    
    
    