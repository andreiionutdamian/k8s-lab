# ToDo
  - [ ] DR

## Traian

```python

# model loading in monitor_app.py

from transformers import AutoTokenizer, AutoModelForSequenceClassification

tokenizer = AutoTokenizer.from_pretrained(model_name, cache_dir=model_cache)
model = AutoModelForSequenceClassification.from_pretrained(model_name, cache_dir=model_cache)

# if everythin was ok now we can commit the result to redis & db

```

### Model loading in serving_app.py

Change requests:
  - move load model in separate mixin - separation of concerns
  - use ultra-low footprint for monitor & use base_th_llm_fastapi for serving
  - add "lambda" model for json model load (identity function: f(x)=x)
  - create non-gpu serving for stg deployment

1. get `model_name`, `model_type` and `model_cache` from redis
2. check if the model_cache folder contains a subfolder that contains model_name (maybe fail)
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

6. Use GPU if available



