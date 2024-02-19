import threading
import json
import time

from paho.mqtt import client as mqttc

from base import BaseMQTT, Printer



# Configuration
MQTT_HOST = '192.168.1.55'
MQTT_PORT = 31883
TOPIC = '/topic_root/subtopic'
THREAD_COUNT = 5  # Number of threads to spawn
package =  "1" * 1_000_000

   
class Publisher(BaseMQTT):
  def __init__(self, *args, **kwargs):
    super(Publisher, self).__init__(*args, **kwargs)
    self.count = 0
    return

  def publish_messages(self):
    """Publish messages with a specific structure."""
    self.P("Starting publisher thread {} ...".format(self.thread_id))
    while True:
      self.count += 1
      payload = json.dumps({
        "sender": self.thread_id,
        "data": package,  # 1 million times '1'
        "id": self.count
      })
      self.publish(payload, TOPIC)
      time.sleep(1)  # Adjust as necessary
    #endwhile
    return

  def run(self):
    """Run the publisher."""
    self.thread = threading.Thread(target=self.publish_messages)
    self.thread.start()
    return

if __name__ == '__main__':
  logger = Printer()

  publishers = []
  for _ in range(THREAD_COUNT):
    publisher = Publisher(
      logger=logger,
      host=MQTT_HOST,
      port=MQTT_PORT,
    )
    publishers.append(publisher)
    publisher.run()
  
  # Assuming you want to join threads, you need to store and join them correctly
  for publisher in publishers:
    # This would require storing the thread object in the Publisher class
    publisher.thread.join()  # Wait for all threads to finish
