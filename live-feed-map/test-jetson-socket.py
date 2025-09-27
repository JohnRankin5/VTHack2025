#!/usr/bin/env python3
"""
Test script to simulate Jetson sending data to the socket server
"""

import socket
import json
import time
import random

def test_socket_connection():
    """Test sending data to the socket server"""
    
    # Connect to the socket server
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 5000))
        print("Connected to socket server on localhost:5000")
        
        # Send test data
        for i in range(10):
            # Simulate sensor data
            sensor_data = {
                'sensor_id': 'RADAR_001',
                'timestamp': time.time(),
                'distance': random.uniform(0.5, 10.0),
                'angle': random.uniform(0, 360),
                'intensity': random.uniform(0, 100),
                'sequence': i + 1
            }
            
            # Send as JSON
            data_json = json.dumps(sensor_data)
            client_socket.send(data_json.encode('utf-8'))
            print(f"Sent: {data_json}")
            
            time.sleep(1)  # Wait 1 second between sends
        
        # Send some raw string data too
        for i in range(5):
            raw_data = f"RAW_SENSOR_DATA_{i+1}:{random.randint(100, 999)}"
            client_socket.send(raw_data.encode('utf-8'))
            print(f"Sent raw: {raw_data}")
            time.sleep(0.5)
        
        client_socket.close()
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")

def test_api_endpoints():
    """Test the HTTP API endpoints"""
    import requests
    
    try:
        # Test health endpoint
        response = requests.get('http://localhost:5001/api/health')
        print(f"Health check: {response.status_code} - {response.json()}")
        
        # Test sensor data endpoint
        response = requests.get('http://localhost:5001/api/sensor-data?count=5')
        print(f"Sensor data: {response.status_code} - {response.json()}")
        
        # Test stats endpoint
        response = requests.get('http://localhost:5001/api/sensor-stats')
        print(f"Stats: {response.status_code} - {response.json()}")
        
    except Exception as e:
        print(f"API test error: {e}")

if __name__ == "__main__":
    print("Testing Jetson Socket Receiver...")
    print("Make sure the socket server is running first!")
    print("Run: python jetson-socket-receiver.py")
    print()
    
    # Test socket connection
    test_socket_connection()
    
    print("\n" + "="*50 + "\n")
    
    # Test API endpoints
    test_api_endpoints()
