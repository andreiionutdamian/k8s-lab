import json
import os
import numpy as np
import pkg_resources
import sys

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

def list_subfolders_files(path='.'):
  """
  Generate lists of all subfolders and files from the specified path.

  Parameters
  ----------
  path : str, optional
    The directory path to start the search from. Defaults to the current directory.

  Returns
  -------
  tuple of list
    A tuple containing two lists: the first list includes all subfolders,
    and the second list includes all files found in the directory and its subdirectories.
  """
  subfolders = []
  files = []

  for dirpath, dirnames, filenames in os.walk(path):
    # Append relative path of subdirectories and files to the respective lists
    for dirname in dirnames:
      subfolders.append(os.path.join(dirpath, dirname))
    for filename in filenames:
      files.append(os.path.join(dirpath, filename))

  return subfolders, files
  

def show_inventory():
  packs = get_packages()
  print("Python version: {}".format(sys.version))
  print("Installed packages:")
  packs = "\n".join(["  " + x for x in packs])
  print("\n".join(packs))
  _, files = list_subfolders_files()
  files = ["  " + x for x in files]
  print("App files:\n{}".format("\n".join(files)))
  return

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

def boxed_print(msg):
  msg_len = len(msg)
  line1 = "#" * 80
  line2 = "#" + " " * 78 + "#"
  line3 = "#" + (78 // 2 - msg_len // 2) * " " + msg + (78 // 2 - msg_len // 2 -1) * " " + "#"
  line4 = "#" + " " * 78 + "#"
  line5 = "#" * 80
  print("\n".join([line1, line2, line3, line4, line5]), flush=True)
  return  
