# ToDo
  - [ ] DR

## Traian

  - [x] add monitor Deployment and serving StatefulSet (carefull with Ingress path overwrite)
  - [x] complete monitor_app.py `maybe_init_models`
  - [x] complete serving_app.py `__get_k8s_status` using kube_mixin.py
  - [x] refactor manifests with shorter names
  - [x] setup RBAC for kube_mixin.py
  - [x] fix PV vs env 
  - [ ] Integrate with HuggingFace models
    - [ ] - modify db: model_type, model_name, model_cache
    - [ ] - monitor service will download/prepare the model:
      - [ ] - a model_cache folder will be assigned by monitor via environment
      - [ ] - model_cache folder will be on mounted volume
      - [ ] - monitor service use HuggingFace api to download the model to model_cache
    - [ ] - monitor service will push to db/redis the new model_type, model_name, model_cache




```python

# model loading in monitor_app.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=model_cache)
model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=model_cache)

# if everythin was ok now we can commit the result to redis & db

```

### Model loading in serving_app.py

1. get `model_name`, `model_type` and `model_cache` from redis
2. check if the model_cache folder contains a subfolder that begins with the model_name (maybe fail)
3. Then load the model from the model_cache folder with same approach as monitor
4. Run the inference on text or image

```python

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline

# 5. start caching area
tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=model_cache)
model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=model_cache)
model_pipeline = pipeline(model_type, model=model, tokenizer=tokenizer)
# 5. end caching area

result = model_pipeline(inputs)

```

5. Reduce model loading redundancy via a hash-table based cache: each time you need to run a loading in serving check if model and tokenizer is not already loaded for that type respecting the latest push from monitor

6. Use GPU is available



