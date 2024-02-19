import json
from collections import defaultdict
import threading
import time
import os

from uuid import uuid4

from base import BaseMQTT, Printer


# Configuration
MQTT_HOST = 'emqx-service'
MQTT_PORT = 1883
TOPIC = '/topic_root/subtopic'


class SimpleListener(BaseMQTT):
  def __init__(self, *args, **kwargs):
    super(SimpleListener, self).__init__(*args, **kwargs)
    self.messages = defaultdict(int)
    self.counters = {}
    return

  def on_message(self, client, userdata, msg, *args, **kwargs):
    """Handle incoming MQTT messages."""
    payload = json.loads(msg.payload)
    sender = payload['sender']
    self.messages[sender] += int(payload['data'][0])  # Increment by the first character converted to int
    self.counters[sender] = payload['id']
    return

  def display_stats(self, ):
    """Periodically display message stats."""
    while True:
      for sender, sum_ in self.messages.items():
        self.P("----------------------------------------")
        self.P(f"{sender} -> sum -> {sum_} (id: {self.counters[sender]})")
      time.sleep(10)  # Adjust as necessary
    return
      
  def run(self):    
    stats_thread = threading.Thread(target=self.display_stats)
    stats_thread.start()

    self.client.loop_forever()
    return
    

if __name__ == '__main__':
  for k, v in os.environ.items():
    if k.startswith('MQTT') or k.startswith('EMQX'):
      print(f"{k}={v}")

  listener = SimpleListener(
    logger=Printer(),
    host=MQTT_HOST,
    port=MQTT_PORT,
    topic=TOPIC,
  )
  listener.run()