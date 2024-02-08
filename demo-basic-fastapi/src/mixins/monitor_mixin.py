import os

from threading import Thread
from time import sleep

class _MonitorMixin:
  def __init__(self, **kwargs):
    self.__done = False
    self.__started = False
    self.__resolution = os.environ.get("MONITOR_RESOLUTION", 1)
    return
  
  
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
  
  
  def monitor_loop(self):    
    while not self.__done:
      sleep(1 / self.__resolution)
    return
    
    