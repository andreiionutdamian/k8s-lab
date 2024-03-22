import os
from datetime import datetime

import torch

from transformers import pipeline
from transformers import AutoTokenizer, AutoConfig, AutoModelForSequenceClassification
from transformers import AutoImageProcessor, AutoModelForImageClassification

class _LlmMixin(object):
  def __init__(self):
    super(_LlmMixin, self).__init__()
    
    self.cache_root = os.getenv('CACHE_ROOT', '.cache')
    return
  
  def load_model(self, model_type: str, model_name: str, returnpipe=False):
    model_cache=f"{self.cache_root}/{model_name}"
    result = None
    self.P(f"Loading model {model_name}....")
    starttime= datetime.now()
    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    try:
      if model_type == "text":
        tokenizer = AutoTokenizer.from_pretrained(
          model_name, cache_dir=model_cache
        )
        #if labels:
        #  rev_labels = dict((v,k) for k,v in labels.items())
        #  config = AutoConfig.from_pretrained(model_name, label2id=rev_labels, id2label=labels)
        #  #config.save_pretrained(model_cache)
        #|  text_model = AutoModelForSequenceClassification.from_pretrained(
        #    model_name, cache_dir=model_cache, config=config
        #  )
        #else:
        text_model = AutoModelForSequenceClassification.from_pretrained(
          model_name, cache_dir=model_cache
        )     
        if returnpipe:
          text_model = text_model.to(device)
          result = pipeline(
            "text-classification", 
            model=text_model, tokenizer=tokenizer, 
            device=device
          )
        else:
          result = True
      elif model_type == "image":
        image_processor = AutoImageProcessor.from_pretrained(
          model_name, cache_dir=model_cache
        )
        image_model =  AutoModelForImageClassification.from_pretrained(
          model_name, cache_dir=model_cache
        )
        if returnpipe:
          image_model=image_model.to(device)
          result = pipeline(
            "image-classification", 
            model=image_model, image_processor=image_processor, 
            device=device
          )
        else:
          result = True
      elif model_type == "json":
        self.P(f"Not implemented {model_type}")
    except Exception as exc:
      self.P("Error load_model: {}".format(exc))
    
    if result:
      endtime= datetime.now()
      duration = endtime-starttime
      self.P(f"Model {model_name} loaded. Elapsed time {duration} ms")
    #endif
    return result