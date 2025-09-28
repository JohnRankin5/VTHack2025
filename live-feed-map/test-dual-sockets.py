#!/usr/bin/env python3
"""
Test script to verify both Jetson and Laptop socket servers are working
"""

import socket
import json
import time
import threading
import random

def test_jetson_socket():
    """Test sending data to Jetson socket (port 65431)"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('10.42.0.117', 65431))
        print("✅ Connected to JETSON socket server on port 65431")
        
        # Send Jetson-style data
        for i in range(5):
            jetson_data = {
                'device_id': 'JETSON_NANO_001',
                'timestamp': time.time(),
                'camera_status': 'active',
                'object_detections': random.randint(0, 5),
                'gesture_detections': random.randint(0, 2),
                'temperature': random.uniform(45.0, 65.0),
                'sequence': i + 1
            }
            
            data_json = json.dumps(jetson_data)
            client_socket.send(data_json.encode('utf-8'))
            print(f"📡 JETSON sent: {data_json}")
            time.sleep(1)
        
        client_socket.close()
        print("✅ JETSON test completed!")
        
    except Exception as e:
        print(f"❌ JETSON socket error: {e}")

def test_laptop_socket():
    """Test sending data to Laptop socket (port 65432)"""
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('10.42.0.117', 65432))
        print("✅ Connected to LAPTOP socket server on port 65432")
        
        # Send Laptop-style data
        for i in range(5):
            laptop_data = {
                'device_id': 'LAPTOP_FIREFIGHTER_002',
                'timestamp': time.time(),
                'location': {'lat': 37.7749 + random.uniform(-0.01, 0.01), 'lon': -122.4194 + random.uniform(-0.01, 0.01)},
                'battery_level': random.randint(20, 100),
                'wifi_signal': random.randint(-80, -30),
                'status': 'operational',
                'sequence': i + 1
            }
            
            data_json = json.dumps(laptop_data)
            client_socket.send(data_json.encode('utf-8'))
            print(f"💻 LAPTOP sent: {data_json}")
            time.sleep(1)
        
        client_socket.close()
        print("✅ LAPTOP test completed!")
        
    except Exception as e:
        print(f"❌ LAPTOP socket error: {e}")

def test_api_endpoints():
    """Test the HTTP API endpoints"""
    import requests
    
    try:
        print("\n🔍 Testing API endpoints...")
        
        # Test health endpoint
        response = requests.get('http://localhost:5003/api/health')
        print(f"🏥 Health check: {response.status_code} - {response.json()}")
        
        # Test sensor data endpoint
        response = requests.get('http://localhost:5003/api/sensor-data?count=10')
        data = response.json()
        print(f"📊 Sensor data: {response.status_code} - Found {data.get('count', 0)} entries")
        
        # Show device breakdown
        if data.get('data'):
            jetson_count = sum(1 for item in data['data'] if item.get('processed_data', {}).get('device_type') == 'jetson')
            laptop_count = sum(1 for item in data['data'] if item.get('processed_data', {}).get('device_type') == 'laptop')
            print(f"   📡 Jetson entries: {jetson_count}")
            print(f"   💻 Laptop entries: {laptop_count}")
        
        # Test stats endpoint
        response = requests.get('http://localhost:5003/api/sensor-stats')
        print(f"📈 Stats: {response.status_code} - {response.json()}")
        
    except Exception as e:
        print(f"❌ API test error: {e}")

if __name__ == "__main__":
    print("🚀 Testing Dual Socket System...")
    print("=" * 60)
    
    # Test both sockets simultaneously
    jetson_thread = threading.Thread(target=test_jetson_socket)
    laptop_thread = threading.Thread(target=test_laptop_socket)
    
    jetson_thread.start()
    laptop_thread.start()
    
    # Wait for both to complete
    jetson_thread.join()
    laptop_thread.join()
    
    print("\n" + "=" * 60)
    
    # Test API endpoints
    time.sleep(2)  # Give servers time to process
    test_api_endpoints()
    
    print("\n🎉 Dual socket test completed!")
