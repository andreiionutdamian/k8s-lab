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
    start = time.time()
    while True:
      good, bad = 0, 0
      counter = 0
      if len(self.messages) == 0:
        time.sleep(1)
        start = time.time()
        continue
      for sender, sum_ in self.messages.items():
        if sum_ == self.counters[sender]:
          good +=1
        else:
          bad += 1
        counter += self.counters[sender]
      msg = "Stats: {} senders, {} stable, {} unstable, {:.0f} msgs/sec".format(
        len(self.messages), 
        good, bad, 
        counter/(time.time()-start))
      self.P(msg)
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