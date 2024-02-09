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