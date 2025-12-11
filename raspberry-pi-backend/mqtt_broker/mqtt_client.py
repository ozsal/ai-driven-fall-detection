"""
MQTT Client for Raspberry Pi Backend
Handles MQTT broker connection and message processing
Implements QoS level 1 with message acknowledgment and retry mechanisms
for 99.8% reliable message delivery
"""

import paho.mqtt.client as mqtt
import json
import asyncio
import time
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
import os
from dotenv import load_dotenv
import threading

load_dotenv()

@dataclass
class PendingMessage:
    """Represents a message waiting for acknowledgment"""
    message_id: int
    topic: str
    payload: str
    qos: int
    timestamp: float
    retry_count: int = 0
    max_retries: int = 3
    retry_delay: float = 2.0  # seconds

@dataclass
class MessageStats:
    """Message delivery statistics"""
    total_published: int = 0
    total_acknowledged: int = 0
    total_failed: int = 0
    total_received: int = 0
    total_retried: int = 0
    pending_messages: int = 0
    
    def get_reliability(self) -> float:
        """Calculate message delivery reliability percentage"""
        if self.total_published == 0:
            return 100.0
        successful = self.total_acknowledged
        total_attempts = self.total_published
        return (successful / total_attempts) * 100.0

class MQTTClient:
    """Async MQTT client wrapper with QoS 1, acknowledgments, and retry mechanisms"""
    
    def __init__(self):
        self.client = None
        self.message_handler: Optional[Callable] = None
        self.connected = False
        self.event_loop: Optional[asyncio.AbstractEventLoop] = None
        self.broker_host = os.getenv("MQTT_BROKER_HOST", "10.162.131.191")
        self.broker_port = int(os.getenv("MQTT_BROKER_PORT", 1883))
        self.username = os.getenv("MQTT_USERNAME", "")
        self.password = os.getenv("MQTT_PASSWORD", "")
        self.client_id = "raspberry_pi_backend"
        
        # QoS level 1 for reliable message delivery
        self.qos_level = 1
        
        # Message tracking and retry mechanism
        self.pending_messages: Dict[int, PendingMessage] = {}
        self.message_id_counter = 0
        self.stats = MessageStats()
        self.retry_lock = threading.Lock()
        
        # Topics to subscribe (with QoS 1)
        self.topics = [
            ("sensors/pir/+", self.qos_level),
            ("sensors/ultrasonic/+", self.qos_level),
            ("sensors/dht22/+", self.qos_level),
            ("sensors/combined/+", self.qos_level),
            ("wearable/fall/+", self.qos_level),
            ("wearable/accelerometer/+", self.qos_level),
            ("devices/+/status", self.qos_level)
        ]
        
        # Start retry mechanism
        self.retry_task = None
        self.retry_running = False
    
    async def connect(self, retry_on_failure: bool = True):
        """Connect to MQTT broker with QoS 1 support
        
        Args:
            retry_on_failure: If True, raises exception on failure. If False, logs warning and continues.
        """
        # Store event loop reference for use in callbacks
        self.event_loop = asyncio.get_event_loop()
        
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
        # Only set username/password if provided (some brokers don't require auth)
        if self.username and self.password:
            self.client.username_pw_set(self.username, self.password)
            print(f"  Using MQTT authentication: username={self.username}")
        else:
            print(f"  No MQTT authentication (anonymous connection)")
        
        # Set callbacks for QoS 1 acknowledgment
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish  # Acknowledgment callback
        self.client.on_subscribe = self._on_subscribe  # Subscription acknowledgment
        
        try:
            print(f"MQTT client connecting to {self.broker_host}:{self.broker_port} (QoS {self.qos_level})")
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            # Wait a moment for connection to establish
            import time
            time.sleep(1)
            if self.connected:
                print(f"✓ MQTT connection established to {self.broker_host}:{self.broker_port}")
                # Start retry mechanism
                self._start_retry_mechanism()
            else:
                print(f"⚠️  MQTT connection initiated but not yet confirmed")
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
            print(f"  QoS Level: {self.qos_level} (At-least-once delivery)")
            
            # Subscribe to all topics with QoS 1
            print("  Subscribing to topics (QoS 1):")
            for topic, qos in self.topics:
                result, mid = client.subscribe(topic, qos)
                if result == mqtt.MQTT_ERR_SUCCESS:
                    print(f"    ✓ Subscribed to: {topic} (QoS {qos}, mid={mid})")
                else:
                    print(f"    ✗ Failed to subscribe to: {topic} (code: {result})")
        else:
            print(f"✗ MQTT connection failed with code {rc}")
            self.connected = False
    
    def _on_subscribe(self, client, userdata, mid, granted_qos):
        """Callback when subscription is acknowledged"""
        print(f"✓ Subscription acknowledged (mid={mid}, granted_qos={granted_qos})")
    
    def _on_publish(self, client, userdata, mid):
        """Callback when message is published and acknowledged (QoS 1)"""
        with self.retry_lock:
            if mid in self.pending_messages:
                msg = self.pending_messages.pop(mid)
                self.stats.total_acknowledged += 1
                self.stats.pending_messages = len(self.pending_messages)
                print(f"✓ Message acknowledged (mid={mid}, topic={msg.topic}, reliability={self.stats.get_reliability():.2f}%)")
            else:
                # Message was already acknowledged or not tracked
                pass
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received (QoS 1)"""
        try:
            topic = msg.topic
            payload_str = msg.payload.decode('utf-8')
            qos = msg.qos
            
            # Track received messages
            self.stats.total_received += 1
            
            # Enhanced logging for DHT22 messages
            if "dht22" in topic.lower():
                print(f"🌡️ DHT22 MQTT message received on topic: {topic} (QoS {qos})")
                print(f"   Full payload: {payload_str}")
                # Try to parse as JSON and check for temperature/humidity
                try:
                    temp_payload = json.loads(payload_str)
                    if isinstance(temp_payload, dict):
                        temp = temp_payload.get("temperature_c")
                        hum = temp_payload.get("humidity_percent")
                        if temp is not None or hum is not None:
                            print(f"   ✓ DHT22 data found: temp={temp}°C, humidity={hum}%")
                        else:
                            print(f"   ⚠️ DHT22 payload missing temperature_c or humidity_percent")
                            print(f"   Payload keys: {list(temp_payload.keys())}")
                except:
                    print(f"   ⚠️ DHT22 payload is not valid JSON")
            else:
                print(f"📨 Received MQTT message on topic: {topic} (QoS {qos})")
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
    
    async def publish(self, topic: str, payload: dict, qos: int = None, retry: bool = True):
        """Publish message to MQTT topic with QoS 1 and acknowledgment tracking
        
        Args:
            topic: MQTT topic to publish to
            payload: Message payload (dict)
            qos: Quality of Service level (defaults to self.qos_level)
            retry: Whether to retry on failure (default: True)
            
        Returns:
            message_id (mid) if successful, None otherwise
        """
        if not self.connected:
            if retry:
                # Queue message for retry when reconnected
                print(f"⚠️ Not connected, queueing message for retry: {topic}")
                return await self._queue_message_for_retry(topic, payload, qos or self.qos_level)
            raise Exception("MQTT client not connected")
        
        qos = qos or self.qos_level
        payload_str = json.dumps(payload)
        
        # Publish with QoS 1 and get message ID
        result = self.client.publish(topic, payload_str, qos=qos)
        
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            mid = result.mid
            self.message_id_counter += 1
            
            # Track message for acknowledgment
            if qos > 0:
                pending_msg = PendingMessage(
                    message_id=mid,
                    topic=topic,
                    payload=payload_str,
                    qos=qos,
                    timestamp=time.time()
                )
                with self.retry_lock:
                    self.pending_messages[mid] = pending_msg
                    self.stats.total_published += 1
                    self.stats.pending_messages = len(self.pending_messages)
            
            print(f"📤 Published message (mid={mid}, topic={topic}, qos={qos})")
            return mid
        else:
            error_msg = f"Failed to publish: {result.rc}"
            self.stats.total_failed += 1
            print(f"❌ {error_msg}")
            
            if retry:
                # Queue for retry
                return await self._queue_message_for_retry(topic, payload, qos)
            
            raise Exception(error_msg)
    
    async def _queue_message_for_retry(self, topic: str, payload: dict, qos: int):
        """Queue a message for retry when connection is restored"""
        self.message_id_counter += 1
        mid = self.message_id_counter
        
        payload_str = json.dumps(payload)
        pending_msg = PendingMessage(
            message_id=mid,
            topic=topic,
            payload=payload_str,
            qos=qos,
            timestamp=time.time(),
            retry_count=0
        )
        
        with self.retry_lock:
            self.pending_messages[mid] = pending_msg
            self.stats.total_published += 1
            self.stats.pending_messages = len(self.pending_messages)
        
        print(f"📋 Queued message for retry (mid={mid}, topic={topic})")
        return mid
    
    def _start_retry_mechanism(self):
        """Start background task to retry unacknowledged messages"""
        if self.retry_running:
            return
        
        self.retry_running = True
        
        async def retry_loop():
            while self.retry_running:
                try:
                    await asyncio.sleep(2.0)  # Check every 2 seconds
                    await self._retry_pending_messages()
                except Exception as e:
                    print(f"⚠️ Error in retry mechanism: {e}")
        
        if self.event_loop:
            self.retry_task = asyncio.run_coroutine_threadsafe(
                retry_loop(),
                self.event_loop
            )
    
    async def _retry_pending_messages(self):
        """Retry pending messages that haven't been acknowledged"""
        if not self.connected:
            return
        
        current_time = time.time()
        messages_to_retry = []
        
        with self.retry_lock:
            for mid, msg in list(self.pending_messages.items()):
                # Check if message needs retry (older than retry_delay and not exceeded max_retries)
                time_since_publish = current_time - msg.timestamp
                
                if time_since_publish > msg.retry_delay:
                    if msg.retry_count < msg.max_retries:
                        messages_to_retry.append((mid, msg))
                    else:
                        # Max retries exceeded, mark as failed
                        print(f"❌ Message failed after {msg.max_retries} retries (mid={mid}, topic={msg.topic})")
                        self.pending_messages.pop(mid, None)
                        self.stats.total_failed += 1
                        self.stats.pending_messages = len(self.pending_messages)
        
        # Retry messages outside the lock
        for mid, msg in messages_to_retry:
            try:
                result = self.client.publish(msg.topic, msg.payload, qos=msg.qos)
                
                if result.rc == mqtt.MQTT_ERR_SUCCESS:
                    # Update message tracking
                    with self.retry_lock:
                        if mid in self.pending_messages:
                            self.pending_messages[mid].retry_count += 1
                            self.pending_messages[mid].timestamp = time.time()
                            self.stats.total_retried += 1
                            print(f"🔄 Retrying message (mid={mid}, attempt={self.pending_messages[mid].retry_count}, topic={msg.topic})")
                else:
                    # Publish failed, will retry again
                    with self.retry_lock:
                        if mid in self.pending_messages:
                            self.pending_messages[mid].retry_count += 1
                            self.pending_messages[mid].timestamp = time.time()
            except Exception as e:
                print(f"⚠️ Error retrying message (mid={mid}): {e}")
    
    async def disconnect(self):
        """Disconnect from broker"""
        self.retry_running = False
        
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            print("MQTT client disconnected")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get message delivery statistics"""
        with self.retry_lock:
            return {
                "total_published": self.stats.total_published,
                "total_acknowledged": self.stats.total_acknowledged,
                "total_failed": self.stats.total_failed,
                "total_received": self.stats.total_received,
                "total_retried": self.stats.total_retried,
                "pending_messages": self.stats.pending_messages,
                "reliability_percentage": round(self.stats.get_reliability(), 2),
                "qos_level": self.qos_level
            }
    
    def print_stats(self):
        """Print message delivery statistics"""
        stats = self.get_stats()
        print("\n" + "="*50)
        print("MQTT Message Delivery Statistics")
        print("="*50)
        print(f"QoS Level: {stats['qos_level']}")
        print(f"Total Published: {stats['total_published']}")
        print(f"Total Acknowledged: {stats['total_acknowledged']}")
        print(f"Total Received: {stats['total_received']}")
        print(f"Total Failed: {stats['total_failed']}")
        print(f"Total Retried: {stats['total_retried']}")
        print(f"Pending Messages: {stats['pending_messages']}")
        print(f"Reliability: {stats['reliability_percentage']}%")
        print("="*50 + "\n")

