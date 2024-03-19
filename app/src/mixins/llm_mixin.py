import os

from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from transformers import AutoImageProcessor

class _LlmMixin(object):
  def __init__(self):
    super(_LlmMixin, self).__init__()
    
    self.cache_root = os.getenv('CACHE_ROOT', '.cache')
    return
  
  def load_model(self, model_type: str, model_name: str, retunpipe=False):
    model_cache=f"{self.cache_root}/{model_name}"
    result = None
    try:
      if model_type == "text":
        tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=model_cache)
        model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=model_cache, trust_remote_code=True)
        result = pipeline("text-classification", model=model, tokenizer=tokenizer) if retunpipe else model
      elif model_type == "image":
        image_processor = AutoImageProcessor.from_pretrained(model_name, cache_dir=model_cache)
        result = image_processor
      elif model_type == "json":
        self.P(f"Not implemented {model_type}")
    except Exception as exc:
      self.P("Error load_model: {}".format(exc))
    return result