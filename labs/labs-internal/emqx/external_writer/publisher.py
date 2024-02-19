import threading
import json
import time
import random
import string
import paho.mqtt.client as mqtt

# Configuration
MQTT_HOST = '192.168.1.55'
MQTT_PORT = 31883
TOPIC = '/topic_root/subtopic'
THREAD_COUNT = 5  # Number of threads to spawn
package =  "1" * 1_000_000

def generate_thread_id():
  """Generate a unique 5 character thread ID."""
  return ''.join(random.choices(string.ascii_letters + string.digits, k=5))

class Publisher:
  def __init__(self):
    self.thread_id = generate_thread_id()
    self.client = mqtt.Client()
    # Define callback for successful connection
    self.client.on_connect = self.on_connect
    # Define callback for disconnection
    self.client.on_disconnect = self.on_disconnect
    try:
      print("Connecting to MQTT broker at {MQTT_HOST}:{MQTT_PORT}", flush=True)
      self.client.connect(MQTT_HOST, MQTT_PORT, 60)
    except Exception as e:
      print(f"Failed to connect to MQTT broker at {MQTT_HOST}:{MQTT_PORT}, error: {e}")
      exit(1)  # Exiting if connection is not successful
    self.count = 0

  def on_connect(self, client, userdata, flags, rc):
    if rc == 0:
      print(f"Connected successfully to {MQTT_HOST}:{MQTT_PORT}")
    else:
      print(f"Failed to connect, return code {rc}")
      # Implement reconnection logic here if necessary

  def on_disconnect(self, client, userdata, rc):
    print(f"Disconnected from MQTT broker with return code {rc}")
    # Implement reconnection logic here

  def publish_messages(self):
    """Publish messages with a specific structure."""
    while True:
      self.count += 1
      payload = json.dumps({
        "sender": self.thread_id,
        "data": package,  # 1 million times '1'
        "id": self.count
      })
      result = self.client.publish(TOPIC, payload)
      # Check if publish was successful
      if result.rc != mqtt.MQTT_ERR_SUCCESS:
        print(f"Failed to publish message to {TOPIC}, error code: {result.rc}")
      time.sleep(1)  # Adjust as necessary

  def run(self):
    """Run the publisher."""
    thread = threading.Thread(target=self.publish_messages)
    thread.start()
    return

if __name__ == '__main__':
  publishers = []
  for _ in range(THREAD_COUNT):
    publisher = Publisher()
    publishers.append(publisher)
    publisher.run()
  
  # Assuming you want to join threads, you need to store and join them correctly
  for publisher in publishers:
    # This would require storing the thread object in the Publisher class
    publisher.thread.join()  # Wait for all threads to finish
