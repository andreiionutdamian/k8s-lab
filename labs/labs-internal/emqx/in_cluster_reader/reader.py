import paho.mqtt.client as mqtt
import json
from collections import defaultdict
import threading
import time
import os

# Configuration
MQTT_HOST = 'emqx-service'
MQTT_PORT = 1883
TOPIC = '/topic_root/subtopic'

messages = defaultdict(int)

def on_message(client, userdata, msg):
  """Handle incoming MQTT messages."""
  payload = json.loads(msg.payload)
  sender = payload['sender']
  messages[sender] += int(payload['data'][0])  # Increment by the first character converted to int

def display_stats():
  """Periodically display message stats."""
  while True:
    for sender, sum_ in messages.items():
      print(f"{sender} -> sum -> {sum_}")
    time.sleep(10)  # Adjust as necessary

if __name__ == '__main__':
  for k, v in os.environ.items():
    if k.startswith('MQTT') or k.startswith('EMQX'):
      print(f"{k}={v}")
      
  client = mqtt.Client()
  client.on_message = on_message
  client.connect(MQTT_HOST, MQTT_PORT, 60)
  client.subscribe(TOPIC)
  
  stats_thread = threading.Thread(target=display_stats)
  stats_thread.start()

  client.loop_forever()
