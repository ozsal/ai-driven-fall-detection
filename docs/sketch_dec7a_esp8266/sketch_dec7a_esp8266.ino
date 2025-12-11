/**
 * ESP8266 Multi-Sensor Node
 * 
 * This code runs on ESP8266 NodeMCU to read:
 * - PIR Motion Sensor (HC-SR501)
 * - Ultrasonic Distance Sensor (HC-SR04)
 * - DHT22 Temperature/Humidity Sensor
 * 
 * Hardware Connections:
 * - PIR OUT: GPIO14 (D5)
 * - Ultrasonic Trig: GPIO12 (D6)
 * - Ultrasonic Echo: GPIO13 (D7)
 * - DHT22 DATA: GPIO4 (D2)
 * 
 * Author: AI Fall Detection System
 * Date: 2024
 */

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// ==================== WiFi Configuration ====================
const char* ssid = "Telnet";
const char* password = "@@Ozsal23##";

// ==================== MQTT Configuration ====================
const char* mqtt_server = "10.162.131.191";  // Raspberry Pi IP address
const int mqtt_port = 1883;
const char* mqtt_user = "";
const char* mqtt_password = "";
const char* mqtt_client_id = "ESP8266_Sensor_Node_01";

// ==================== Sensor Pin Definitions ====================
#define PIR_PIN 14          // GPIO14 (D5) - PIR motion sensor
#define ULTRASONIC_TRIG 12  // GPIO12 (D6) - Ultrasonic trigger
#define ULTRASONIC_ECHO 13  // GPIO13 (D7) - Ultrasonic echo
#define DHT_PIN 4           // GPIO4 (D2) - DHT22 data pin
#define LED_PIN 2           // GPIO2 (D4) - Built-in LED

// ==================== Sensor Configuration ====================
#define DHT_TYPE DHT22
DHT dht(DHT_PIN, DHT_TYPE);

// ==================== Global Variables ====================
WiFiClient espClient;
PubSubClient client(espClient);

unsigned long lastMsg = 0;
const unsigned long SENSOR_INTERVAL = 2000;  // Read sensors every 2 seconds
const unsigned long RECONNECT_INTERVAL = 5000;  // Reconnect every 5 seconds if disconnected

// Device identification
const char* device_id = "ESP8266_NODE_01";
const char* location = "Living_Room";

// Sensor state
bool pirState = false;
bool lastPirState = false;
float distance = 0.0;
float temperature = 0.0;
float humidity = 0.0;

// ==================== Function Prototypes ====================
void setup_wifi();
void reconnect_mqtt();
void read_sensors();
void publish_sensor_data();
float read_ultrasonic_distance();
void blink_led(int times, int delay_ms);

// ==================== Setup Function ====================
void setup() {
  Serial.begin(115200);
  delay(100);
  
  Serial.println("\n\n=== ESP8266 Multi-Sensor Node Starting ===");
  Serial.println("Device ID: " + String(device_id));
  Serial.println("Location: " + String(location));
  
  // Initialize pins
  pinMode(PIR_PIN, INPUT);
  pinMode(ULTRASONIC_TRIG, OUTPUT);
  pinMode(ULTRASONIC_ECHO, INPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Initialize DHT22
  dht.begin();
  delay(2000);  // Give DHT22 sensor time to stabilize (recommended: 2 seconds)
  Serial.println("DHT22 sensor initialized");
  
  // Initial LED blink
  blink_led(3, 200);
  
  // Connect to WiFi
  setup_wifi();
  
  // Setup MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(mqtt_callback);
  
  Serial.println("Setup complete. Starting main loop...");
}

// ==================== Main Loop ====================
void loop() {
  // Maintain MQTT connection
  if (!client.connected()) {
    reconnect_mqtt();
  }
  client.loop();
  
  // Read and publish sensor data at intervals
  unsigned long now = millis();
  if (now - lastMsg > SENSOR_INTERVAL) {
    lastMsg = now;
    
    read_sensors();
    publish_sensor_data();
    
    // Blink LED to indicate activity
    digitalWrite(LED_PIN, LOW);
    delay(50);
    digitalWrite(LED_PIN, HIGH);
  }
}

// ==================== WiFi Setup ====================
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);
  
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
    blink_led(1, 100);
  }
  
  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("");
    Serial.println("WiFi connected!");
    Serial.print("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.print("Signal strength (RSSI): ");
    Serial.print(WiFi.RSSI());
    Serial.println(" dBm");
    blink_led(5, 100);  // Success indicator
  } else {
    Serial.println("\nWiFi connection failed!");
    Serial.println("Retrying in 5 seconds...");
    delay(5000);
    setup_wifi();  // Retry
  }
}

// ==================== MQTT Reconnection ====================
void reconnect_mqtt() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    
    if (client.connect(mqtt_client_id, mqtt_user, mqtt_password)) {
      Serial.println("connected!");
      
      // Subscribe to control topics
      String subscribe_topic = "devices/" + String(device_id) + "/control";
      client.subscribe(subscribe_topic.c_str());
      Serial.println("Subscribed to: " + subscribe_topic);
      
      // Publish online status
      String status_topic = "devices/" + String(device_id) + "/status";
      client.publish(status_topic.c_str(), "online");
      
      blink_led(2, 200);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" retrying in 5 seconds");
      delay(5000);
    }
  }
}

// ==================== MQTT Callback ====================
void mqtt_callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println(message);
  
  // Handle control messages
  if (String(topic).indexOf("control") >= 0) {
    if (message == "reset") {
      ESP.restart();
    } else if (message == "read_now") {
      read_sensors();
      publish_sensor_data();
    }
  }
}

// ==================== Read All Sensors ====================
void read_sensors() {
  // Read PIR sensor
  pirState = digitalRead(PIR_PIN);
  
  // Read ultrasonic distance
  distance = read_ultrasonic_distance();
  
  // Read DHT22 (temperature and humidity)
  // Add small delay before reading to ensure sensor is ready
  delay(100);
  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  
  // Check if DHT22 read was successful and within valid ranges
  if (!isnan(temp) && !isnan(hum) && temp > -40 && temp < 80 && hum >= 0 && hum <= 100) {
    temperature = temp;
    humidity = hum;
    Serial.print("✓ DHT22 read successful: ");
    Serial.print(temperature);
    Serial.print("°C, ");
    Serial.print(humidity);
    Serial.println("%");
  } else {
    Serial.println("✗ Failed to read from DHT22 sensor!");
    Serial.print("  Raw temp: ");
    Serial.println(temp);
    Serial.print("  Raw humidity: ");
    Serial.println(hum);
    // Reset to 0.0 to indicate invalid reading
    temperature = 0.0;
    humidity = 0.0;
  }
  
  // Print sensor readings to serial
  Serial.println("\n--- Sensor Readings ---");
  Serial.print("PIR Motion: ");
  Serial.println(pirState ? "DETECTED" : "NO MOTION");
  Serial.print("Distance: ");
  Serial.print(distance);
  Serial.println(" cm");
  Serial.print("Temperature: ");
  Serial.print(temperature);
  Serial.println(" °C");
  Serial.print("Humidity: ");
  Serial.print(humidity);
  Serial.println(" %");
  
  // Check for PIR state change
  if (pirState != lastPirState) {
    Serial.println("PIR state changed!");
    lastPirState = pirState;
  }
}

// ==================== Read Ultrasonic Distance ====================
float read_ultrasonic_distance() {
  // Clear trigger pin
  digitalWrite(ULTRASONIC_TRIG, LOW);
  delayMicroseconds(2);
  
  // Set trigger pin HIGH for 10 microseconds
  digitalWrite(ULTRASONIC_TRIG, HIGH);
  delayMicroseconds(10);
  digitalWrite(ULTRASONIC_TRIG, LOW);
  
  // Read echo pin, returns sound wave travel time in microseconds
  long duration = pulseIn(ULTRASONIC_ECHO, HIGH, 30000);  // 30ms timeout
  
  // Calculate distance (speed of sound = 343 m/s = 0.0343 cm/μs)
  // Distance = (duration * 0.0343) / 2
  float distance_cm = (duration * 0.0343) / 2.0;
  
  // Validate reading (HC-SR04 range: 2cm to 400cm)
  if (distance_cm < 2.0 || distance_cm > 400.0) {
    return -1.0;  // Invalid reading
  }
  
  return distance_cm;
}

// ==================== Publish Sensor Data to MQTT ====================
void publish_sensor_data() {
  // Create JSON document
  StaticJsonDocument<512> doc;
  
  doc["device_id"] = device_id;
  doc["location"] = location;
  doc["timestamp"] = millis();
  doc["sensors"]["pir"]["motion_detected"] = pirState;
  doc["sensors"]["ultrasonic"]["distance_cm"] = distance;
  doc["sensors"]["dht22"]["temperature_c"] = temperature;
  doc["sensors"]["dht22"]["humidity_percent"] = humidity;
  doc["wifi"]["rssi"] = WiFi.RSSI();
  
  // Serialize JSON to string
  char json_buffer[512];
  serializeJson(doc, json_buffer);
  
  // Publish to MQTT topics - each sensor separately
  String topic_pir = "sensors/pir/" + String(device_id);
  String topic_ultrasonic = "sensors/ultrasonic/" + String(device_id);
  String topic_dht22 = "sensors/dht22/" + String(device_id);
  String topic_combined = "sensors/combined/" + String(device_id);
  
  // Publish PIR sensor data (motion detected: 1 or 0)
  client.publish(topic_pir.c_str(), pirState ? "1" : "0");
  Serial.print("Published PIR: ");
  Serial.println(pirState ? "1" : "0");
  
  // Publish Ultrasonic sensor data (distance in cm)
  client.publish(topic_ultrasonic.c_str(), String(distance).c_str());
  Serial.print("Published Ultrasonic: ");
  Serial.println(distance);
  
  // Publish DHT22 sensor data (temperature and humidity as JSON)
  // Only publish if we have valid temperature and humidity readings (both must be valid)
  if (temperature != 0.0 && humidity != 0.0) {
    StaticJsonDocument<256> dht22_doc;
    dht22_doc["device_id"] = device_id;
    dht22_doc["temperature_c"] = temperature;
    dht22_doc["humidity_percent"] = humidity;
    dht22_doc["timestamp"] = millis();
    char dht22_buffer[256];
    serializeJson(dht22_doc, dht22_buffer);
    
    bool published = client.publish(topic_dht22.c_str(), dht22_buffer);
    if (published) {
      Serial.print("✓ Published DHT22: ");
      Serial.println(dht22_buffer);
    } else {
      Serial.println("✗ Failed to publish DHT22 data to MQTT!");
      Serial.print("  Topic: ");
      Serial.println(topic_dht22);
      Serial.print("  Payload: ");
      Serial.println(dht22_buffer);
    }
  } else {
    Serial.println("⚠️ Skipping DHT22 publish - invalid sensor readings (temp=0.0, humidity=0.0)");
    Serial.println("  Check DHT22 sensor connection and wiring!");
  }
  
  // Publish combined JSON data (all sensors together)
  client.publish(topic_combined.c_str(), json_buffer);
  Serial.print("Published Combined: ");
  Serial.println(json_buffer);
  
  Serial.println("All sensor data published to MQTT");
}

// ==================== LED Blink Helper ====================
void blink_led(int times, int delay_ms) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, LOW);
    delay(delay_ms);
    digitalWrite(LED_PIN, HIGH);
    delay(delay_ms);
  }
}

