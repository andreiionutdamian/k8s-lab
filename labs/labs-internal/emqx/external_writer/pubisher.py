import threading
import json
import time
import random
import string
import paho.mqtt.client as mqtt

# Configuration
MQTT_HOST = '192.168.1.55'
MQTT_PORT = 1883
TOPIC = '/topic_root/subtopic'
THREAD_COUNT = 5  # Number of threads to spawn
package =  "1" * 1_000_000

def publish_messages(thread_id):
  """Publish messages with a specific structure."""
  client = mqtt.Client()
  client.connect(MQTT_HOST, MQTT_PORT, 60)
  count = 0
  while True:
    count += 1
    payload = json.dumps({
      "sender": thread_id,
      "data": package,  # 1 million times '1'
      "id": count
    })
    client.publish(TOPIC, payload)
    time.sleep(1)  # Adjust as necessary

def generate_thread_id():
  """Generate a unique 5 character thread ID."""
  return ''.join(random.choices(string.ascii_letters + string.digits, k=5))

if __name__ == '__main__':
  threads = []
  for _ in range(THREAD_COUNT):
    thread_id = generate_thread_id()
    thread = threading.Thread(target=publish_messages, args=(thread_id,))
    thread.start()
    threads.append(thread)

  for thread in threads:
    thread.join()
