import json
import numpy as np
import pkg_resources

from datetime import datetime

def get_packages(monitored_packages=None):
  packs = [x for x in pkg_resources.working_set]
  maxlen = max([len(x.key) for x in packs]) + 1
  if isinstance(monitored_packages, list) and len(monitored_packages) > 0:
    packs = [
        "{}{}".format(x.key + ' ' * (maxlen - len(x.key)), x.version) for x in packs
        if x.key in monitored_packages
    ]
  else:
    packs = [
        "{}{}".format(x.key + ' ' * (maxlen - len(x.key)), x.version) for x in packs
    ]
  packs = sorted(packs)
  return packs

class NPJson(json.JSONEncoder):
  """
  Used to help jsonify numpy arrays or lists that contain numpy data types.
  """
  def default(self, obj):
      if isinstance(obj, np.integer):
          return int(obj)
      elif isinstance(obj, np.floating):
          return float(obj)
      elif isinstance(obj, np.ndarray):
          return obj.tolist()
      elif isinstance(obj, np.ndarray):
          return obj.tolist()
      elif isinstance(obj, datetime):
          return obj.strftime("%Y-%m-%d %H:%M:%S")
      else:
          return super(NPJson, self).default(obj)
        
def safe_jsonify(obj, indent=2, **kwargs):
  """
  Safely jsonify an object, including numpy arrays or lists that contain numpy data types.
  """
  return json.dumps(obj, cls=NPJson, indent=indent, **kwargs)
