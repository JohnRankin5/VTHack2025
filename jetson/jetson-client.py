#!/usr/bin/env python3
"""
Jetson Client - Send data to the socket server
Use this on your Jetson device to send sensor data to the main server
"""

import socket
import json
import time
import random

# Configuration
SERVER_HOST = "10.42.0.117"   # Your main server IP
SERVER_PORT = 65431           # Jetson port
DEVICE_ID = "JETSON_NANO_001"  # Unique device identifier

def connect_to_server():
    """Connect to the main server"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"✅ Connected to server at {SERVER_HOST}:{SERVER_PORT}")
        return client_socket
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

def send_sensor_data(socket_conn):
    """Send sensor data to server"""
    try:
        # Example sensor data from Jetson
        sensor_data = {
            'device_id': DEVICE_ID,
            'timestamp': time.time(),
            'device_type': 'jetson',
            'camera_status': 'active',
            'object_detections': random.randint(0, 10),
            'gesture_detections': random.randint(0, 3),
            'temperature': random.uniform(45.0, 70.0),
            'cpu_usage': random.uniform(20.0, 80.0),
            'memory_usage': random.uniform(30.0, 90.0),
            'location': {
                'building': 'Building A',
                'floor': 2,
                'room': 'Office 201'
            }
        }
        
        # Send as JSON
        data_json = json.dumps(sensor_data)
        socket_conn.send(data_json.encode('utf-8'))
        print(f"📡 Sent: {data_json}")
        return True
        
    except Exception as e:
        print(f"❌ Send error: {e}")
        return False

def main():
    """Main loop"""
    print(f"🚀 Starting Jetson Client - {DEVICE_ID}")
    print(f"📡 Connecting to {SERVER_HOST}:{SERVER_PORT}")
    
    while True:
        # Connect to server
        socket_conn = connect_to_server()
        if not socket_conn:
            print("⏳ Retrying in 5 seconds...")
            time.sleep(5)
            continue
        
        try:
            # Send data every 2 seconds
            while True:
                if not send_sensor_data(socket_conn):
                    break
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            socket_conn.close()
            print("🔌 Disconnected from server")
            time.sleep(5)  # Wait before reconnecting

if __name__ == "__main__":
    main()
