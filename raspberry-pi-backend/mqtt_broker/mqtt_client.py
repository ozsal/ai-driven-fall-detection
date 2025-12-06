"""
MQTT Client for Raspberry Pi Backend
Handles MQTT broker connection and message processing
"""

import paho.mqtt.client as mqtt
import json
import asyncio
import time
from typing import Callable, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class MQTTClient:
    """Async MQTT client wrapper"""
    
    def __init__(self):
        self.client = None
        self.message_handler: Optional[Callable] = None
        self.connected = False
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.broker_host = os.getenv("MQTT_BROKER_HOST", "10.162.131.191")
        self.broker_port = int(os.getenv("MQTT_BROKER_PORT", 8883))
        self.username = os.getenv("MQTT_USERNAME", "ozsal")
        self.password = os.getenv("MQTT_PASSWORD", "@@Ozsal23##")
        self.client_id = "raspberry_pi_backend"
        
        # Topics to subscribe
        self.topics = [
            "sensors/pir/+",
            "sensors/ultrasonic/+",
            "sensors/dht22/+",
            "sensors/combined/+",
            "wearable/fall/+",
            "wearable/accelerometer/+",
            "devices/+/status"
        ]
    
    async def connect(self, retry_on_failure: bool = True):
        """Connect to MQTT broker
        
        Args:
            retry_on_failure: If True, raises exception on failure. If False, logs warning and continues.
        """
        # Store event loop reference for use in callbacks
        self.event_loop = asyncio.get_event_loop()
        
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.username_pw_set(self.username, self.password)
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            print(f"MQTT client connecting to {self.broker_host}:{self.broker_port}")
        except Exception as e:
            error_msg = f"MQTT connection error: {e}"
            print(f"⚠️  {error_msg}")
            print(f"⚠️  MQTT broker at {self.broker_host}:{self.broker_port} is not available")
            print(f"⚠️  API will continue without MQTT. Sensor data will not be received until MQTT is available.")
            if retry_on_failure:
                raise
            # Don't raise - allow API to continue without MQTT
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker"""
        if rc == 0:
            self.connected = True
            print("✓ MQTT client connected successfully")
            print(f"  Broker: {self.broker_host}:{self.broker_port}")
            
            # Subscribe to all topics
            print("  Subscribing to topics:")
            for topic in self.topics:
                result = client.subscribe(topic)
                if result[0] == 0:
                    print(f"    ✓ Subscribed to: {topic}")
                else:
                    print(f"    ✗ Failed to subscribe to: {topic} (code: {result[0]})")
        else:
            print(f"✗ MQTT connection failed with code {rc}")
            self.connected = False
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            topic = msg.topic
            payload_str = msg.payload.decode('utf-8')
            print(f"📨 Received MQTT message on topic: {topic}")
            print(f"   Payload: {payload_str[:100]}...")  # Print first 100 chars
            
            # Try to parse as JSON
            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError:
                # If not JSON, create simple dict
                payload = {"value": payload_str, "raw": payload_str}
            
            # Ensure payload is a dictionary (JSON can parse to primitives like int, float, str)
            if not isinstance(payload, dict):
                if isinstance(payload, (int, float)):
                    payload = {"value": payload, "raw": payload}
                elif isinstance(payload, str):
                    payload = {"value": payload, "raw": payload}
                else:
                    # Try to convert to dict if possible
                    try:
                        payload = dict(payload)
                    except:
                        payload = {"value": str(payload), "raw": payload}
            
            # Add topic information
            payload["topic"] = topic
            payload["received_at"] = time.time()  # Use time.time() instead of event loop time
            
            # Call message handler if set
            if self.message_handler and self.event_loop:
                try:
                    print(f"🔄 Scheduling message handler for topic: {topic}")
                    # Use run_coroutine_threadsafe to safely schedule in the main event loop
                    # Don't wait for result here - let it run asynchronously
                    # The handler will log its own success/failure
                    future = asyncio.run_coroutine_threadsafe(
                        self.message_handler(topic, payload),
                        self.event_loop
                    )
                    # Add a callback to log completion (optional, for debugging)
                    def log_completion(fut):
                        try:
                            fut.result()  # This will raise if there was an exception
                            print(f"✅ Message handler completed for topic: {topic}")
                        except Exception as e:
                            print(f"❌ Message handler failed for topic {topic}: {e}")
                            import traceback
                            traceback.print_exc()
                    future.add_done_callback(log_completion)
                except Exception as e:
                    print(f"❌ Error scheduling message handler: {e}")
                    import traceback
                    traceback.print_exc()
            elif self.message_handler:
                print("⚠️ Warning: Event loop not available, cannot process message")
            else:
                print("⚠️ Warning: No message handler set, message will not be processed")
            
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected"""
        self.connected = False
        print(f"MQTT client disconnected (rc={rc})")
    
    def set_message_handler(self, handler: Callable):
        """Set async message handler function"""
        self.message_handler = handler
    
    def is_connected(self) -> bool:
        """Check if connected to broker"""
        if not self.client:
            return False
        try:
            return self.connected and self.client.is_connected()
        except:
            return False
    
    async def publish(self, topic: str, payload: dict):
        """Publish message to MQTT topic"""
        if not self.connected:
            raise Exception("MQTT client not connected")
        
        payload_str = json.dumps(payload)
        result = self.client.publish(topic, payload_str)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            return True
        else:
            raise Exception(f"Failed to publish: {result.rc}")
    
    async def disconnect(self):
        """Disconnect from broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            print("MQTT client disconnected")

