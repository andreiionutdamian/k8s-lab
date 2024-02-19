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

def on_connect(client, userdata, flags, rc):
  """Callback for when the client receives a CONNACK response from the server."""
  if rc == 0:
    print(f"Connected successfully to {MQTT_HOST}:{MQTT_PORT}")
    client.subscribe(TOPIC)  # Move subscription to here to ensure it's effective after a successful connect
  else:
    print(f"Failed to connect, return code {rc}")
    # Implement reconnection logic here if necessary

def on_disconnect(client, userdata, rc):
  """Callback for when the client disconnects from the broker."""
  if rc != 0:
    print(f"Unexpected disconnection.")
    # Implement reconnection logic here

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
  # Assign the callbacks
  client.on_connect = on_connect
  client.on_disconnect = on_disconnect
  client.on_message = on_message

  try:
    client.connect(MQTT_HOST, MQTT_PORT, 60)
  except Exception as e:
    print(f"Failed to connect to MQTT broker at {MQTT_HOST}:{MQTT_PORT}, error: {e}")
    exit(1)  # Exiting if connection is not successful
  
  stats_thread = threading.Thread(target=display_stats)
  stats_thread.start()

  client.loop_forever()
