import threading
import random
import string
import time


from paho.mqtt import client as mqttc
from paho.mqtt import __version__ as mqtt_version

__VER__ = '0.1.2'



def generate_thread_id():
  """Generate a unique 5 character thread ID."""
  return ''.join(random.choices(string.ascii_letters + string.digits, k=5))


class Printer:
  def __init__(self):
    self.lock = threading.Lock()
    return
  
  def print_message(self, message):
    self.lock.acquire()
    print(message, flush=True)
    self.lock.release()
    return
  
  
class BaseMQTT:
  def __init__(self, logger, host, port, topic=None, retry=5, retry_delay=5):    
    self.logger = logger
    self.client = None
    self.P(f"{self.__class__.__name__} v{__VER__} using paho-mqtt version {mqtt_version}")
    self.host = host
    self.port = port
    self.topic = topic
    self.thread_id = generate_thread_id()
    for _ in range(retry):
      connected = self.__connect()
      if connected:
        break          
      time.sleep(retry_delay)
    if not connected:
      msg = f"Failed to connect to {self.host}:{self.port} after {retry} attempts"
      raise ValueError(msg)  
    return  
  
  
  def P(self, msg):
    self.logger.print_message(msg)
    return
  
  def __connect(self):
    result = False
    try:
      self.create_client()
      self.P(f"Connecting to MQTT broker at {self.host}:{self.port}")
      self.client.connect(self.host, self.port, 60)
      result = True
    except Exception as e:
      self.P(f"Failed to connect to MQTT broker at {self.host}:{self.port}, error: {e}")
    return result# Exiting if connection is not successful
  
 # Paho MQTT client creation v1 vs v2
  def create_client(self):    
    if self.client is not None:
      return
    if mqtt_version.startswith('2'):
      kwargs = dict(
        callback_api_version=mqttc.CallbackAPIVersion.VERSION2,
        client_id=self.thread_id, 
        clean_session=True,
      )
    else:
      kwargs = mqttc.Client(
        client_id=self.listener_id, 
        clean_session=True,
      )
    #endif v2 vs v1
    self.client = mqttc.Client(**kwargs) 
    self.client.on_message = self.on_message
    self.client.on_connect = self.on_connect
    self.client.on_disconnect = self.on_disconnect
    return
  
  
  def publish(self, payload, topic):
    """Publish a message to the broker."""
    res = self.client.publish(topic, payload)
    # Check if publish was successful
    if res.rc != mqttc.MQTT_ERR_SUCCESS:
      self.P(f"Failed to publish message to {topic}, error code: {res.rc}")
      result = True
    else:
      result = False      
    return result
  

  def on_message(self, client, userdata, msg, *args, **kwargs):
    """Handle incoming MQTT messages."""
    return
  
  
  def on_connect(self, client, userdata, flags, reason_code, *args, **kwargs):
    """Callback for when the client receives a CONNACK response from the server."""
    if reason_code == 0:
      self.P(f"Connected successfully to {self.host}:{self.port}")
      if self.topic:
        # Move subsription to here to ensure it's effective after a successful connect
        client.subscribe(self.topic)  
    else:
      self.P(f"Failed to connect, return code {reason_code}")
      # Implement reconnection logic here if necessary
    return


  def on_disconnect(self, client, userdata, reason_code, *args, **kwargs):
    """Callback for when the client disconnects from the broker."""
    if reason_code != 0:
      self.P(f"Unexpected disconnection. Code: {reason_code}")
      # Implement reconnection logic here
    else:
      self.P(f"Disconnected from {self.host}:{self.port}")
    return  
      