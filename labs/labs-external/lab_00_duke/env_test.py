try:
  import torch as th
except:
  th = None
import sys


if __name__ == '__main__':
  print("Python version:     {}".format(sys.version))
  if th is not None:
    print("Torch version:      {}".format(th.__version__))
    print("CUDA available:     {}".format(th.cuda.is_available()))
    if th.cuda.is_available():
      print("  GPU device name:  {}".format(th.cuda.get_device_name(0)))
      print("  GPU memory total: {:.1f} GB".format(th.cuda.get_device_properties(0).total_memory / (1024**3)))
  else:
    print("Torch not available")