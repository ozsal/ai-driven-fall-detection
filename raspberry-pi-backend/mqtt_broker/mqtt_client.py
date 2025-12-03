"""
MQTT Client for Raspberry Pi Backend
Handles MQTT broker connection and message processing
"""

import paho.mqtt.client as mqtt
import json
import asyncio
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
        self.broker_host = os.getenv("MQTT_BROKER_HOST", "localhost")
        self.broker_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
        self.username = os.getenv("MQTT_USERNAME", "admin")
        self.password = os.getenv("MQTT_PASSWORD", "admin_password")
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
    
    async def connect(self):
        """Connect to MQTT broker"""
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
            print(f"MQTT connection error: {e}")
            raise
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to broker"""
        if rc == 0:
            self.connected = True
            print("MQTT client connected successfully")
            
            # Subscribe to all topics
            for topic in self.topics:
                client.subscribe(topic)
                print(f"Subscribed to: {topic}")
        else:
            print(f"MQTT connection failed with code {rc}")
            self.connected = False
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            topic = msg.topic
            payload_str = msg.payload.decode('utf-8')
            
            # Try to parse as JSON
            try:
                payload = json.loads(payload_str)
            except json.JSONDecodeError:
                # If not JSON, create simple dict
                payload = {"value": payload_str, "raw": payload_str}
            
            # Add topic information
            payload["topic"] = topic
            payload["received_at"] = asyncio.get_event_loop().time()
            
            # Call message handler if set
            if self.message_handler:
                # Run handler in event loop
                asyncio.create_task(self.message_handler(topic, payload))
            
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
        return self.connected and self.client.is_connected()
    
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

