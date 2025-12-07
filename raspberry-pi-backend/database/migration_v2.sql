-- Migration Script: Extend Database Schema v2
-- This script adds new tables and modifies existing ones
-- Run this AFTER backing up your database

-- ============================================
-- 1. Update devices table (add device_name, modify structure)
-- ============================================
-- Add device_name column if it doesn't exist
ALTER TABLE devices ADD COLUMN device_name TEXT;
ALTER TABLE devices ADD COLUMN id INTEGER;

-- Create new devices table structure (if needed)
-- Note: We'll handle this in Python migration to preserve existing data

-- ============================================
-- 2. Update sensors table (add sensor_name, link to devices.id)
-- ============================================
ALTER TABLE sensors ADD COLUMN sensor_name TEXT;
ALTER TABLE sensors ADD COLUMN device_id_fk INTEGER;  -- Foreign key to devices.id

-- ============================================
-- 3. Create new sensor-specific reading tables
-- ============================================

-- PIR readings table
CREATE TABLE IF NOT EXISTS pir_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    motion_detected INTEGER NOT NULL,  -- 0 or 1 (boolean)
    timestamp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);

-- Ultrasonic readings table
CREATE TABLE IF NOT EXISTS ultrasonic_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    distance_cm REAL NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);

-- DHT22 readings table
CREATE TABLE IF NOT EXISTS dht22_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    temperature_c REAL NOT NULL,
    humidity_percent REAL NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);

-- WiFi readings table
CREATE TABLE IF NOT EXISTS wifi_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id INTEGER NOT NULL,
    rssi INTEGER NOT NULL,
    timestamp INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
);

-- ============================================
-- 4. Create indexes for performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_pir_sensor ON pir_readings(sensor_id);
CREATE INDEX IF NOT EXISTS idx_pir_timestamp ON pir_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_ultrasonic_sensor ON ultrasonic_readings(sensor_id);
CREATE INDEX IF NOT EXISTS idx_ultrasonic_timestamp ON ultrasonic_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_dht22_sensor ON dht22_readings(sensor_id);
CREATE INDEX IF NOT EXISTS idx_dht22_timestamp ON dht22_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_wifi_sensor ON wifi_readings(sensor_id);
CREATE INDEX IF NOT EXISTS idx_wifi_timestamp ON wifi_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensors_device_fk ON sensors(device_id_fk);

