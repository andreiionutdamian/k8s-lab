import paho
import paho.mqtt.client as mqtt
import json
from collections import defaultdict
import threading
import time
import os

from uuid import uuid4

print("Using paho-mqtt version", paho.__version__, flush=True)

# Configuration
MQTT_HOST = '192.168.1.55' #'emqx-service'
MQTT_PORT = 31883 #1883
TOPIC = '/topic_root/subtopic'



class SimpleListener:
  def __init__(self):
    self.listener_id = str(uuid4())[:5]
    self.messages = defaultdict(int)
    self.client = mqtt.Client(
      client_id=self.listener_id,
      clean_session=True      
    )
    # Assign the callbacks
    self.client.on_connect = self.on_connect
    self.client.on_disconnect = self.on_disconnect
    self.client.on_message = self.on_message
    return

  def on_connect(self, client, userdata, flags, rc):
    """Callback for when the client receives a CONNACK response from the server."""
    if rc == 0:
      print(f"Connected successfully to {MQTT_HOST}:{MQTT_PORT}")
      client.subscribe(TOPIC)  # Move subscription to here to ensure it's effective after a successful connect
    else:
      print(f"Failed to connect, return code {rc}")
      # Implement reconnection logic here if necessary
    return

  def on_disconnect(self, client, userdata, rc):
    """Callback for when the client disconnects from the broker."""
    if rc != 0:
      print(f"Unexpected disconnection.")
      # Implement reconnection logic here
    return

  def on_message(self, client, userdata, msg):
    """Handle incoming MQTT messages."""
    payload = json.loads(msg.payload)
    sender = payload['sender']
    self.messages[sender] += int(payload['data'][0])  # Increment by the first character converted to int
    return

  def display_stats(self, ):
    """Periodically display message stats."""
    while True:
      for sender, sum_ in self.messages.items():
        print(f"{sender} -> sum -> {sum_}")
      time.sleep(10)  # Adjust as necessary
    return
      
  def run(self):
    try:
      self.client.connect(MQTT_HOST, MQTT_PORT, 60)
    except Exception as e:
      print(f"Failed to connect to MQTT broker at {MQTT_HOST}:{MQTT_PORT}, error: {e}")
      exit(1)  # Exiting if connection is not successful
    
    stats_thread = threading.Thread(target=self.display_stats)
    stats_thread.start()

    self.client.loop_forever()
    return
    

if __name__ == '__main__':
  for k, v in os.environ.items():
    if k.startswith('MQTT') or k.startswith('EMQX'):
      print(f"{k}={v}")


  listener = SimpleListener()
  listener.run()