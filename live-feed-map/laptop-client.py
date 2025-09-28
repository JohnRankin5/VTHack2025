#!/usr/bin/env python3
"""
Laptop Client - Send data to the socket server
Use this on firefighter laptops to send status data to the main server
"""

import socket
import json
import time
import random
import platform

# Configuration
SERVER_HOST = "10.42.0.117"   # Your main server IP
SERVER_PORT = 65432           # Laptop port
DEVICE_ID = f"LAPTOP_{platform.node().upper()}"  # Use computer name as ID

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

def get_system_info():
    """Get basic system information"""
    import psutil
    try:
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'battery_percent': psutil.sensors_battery().percent if psutil.sensors_battery() else None,
            'disk_usage': psutil.disk_usage('/').percent
        }
    except:
        return {
            'cpu_percent': random.uniform(10, 80),
            'memory_percent': random.uniform(20, 70),
            'battery_percent': random.randint(20, 100),
            'disk_usage': random.uniform(30, 80)
        }

def send_status_data(socket_conn):
    """Send laptop status data to server"""
    try:
        system_info = get_system_info()
        
        # Example laptop data
        status_data = {
            'device_id': DEVICE_ID,
            'timestamp': time.time(),
            'device_type': 'laptop',
            'firefighter_id': 'FF-002',
            'status': 'operational',
            'location': {
                'lat': 37.7749 + random.uniform(-0.01, 0.01),  # San Francisco area
                'lon': -122.4194 + random.uniform(-0.01, 0.01),
                'building': 'Emergency Command Center',
                'floor': 1
            },
            'system': system_info,
            'network': {
                'wifi_signal': random.randint(-80, -30),
                'connection_type': 'wifi',
                'bandwidth': random.uniform(10, 100)
            },
            'applications': {
                'live_feed_active': True,
                'map_view_active': True,
                'communication_active': True
            }
        }
        
        # Send as JSON
        data_json = json.dumps(status_data)
        socket_conn.send(data_json.encode('utf-8'))
        print(f"💻 Sent: {json.dumps(status_data, indent=2)}")
        return True
        
    except Exception as e:
        print(f"❌ Send error: {e}")
        return False

def main():
    """Main loop"""
    print(f"🚀 Starting Laptop Client - {DEVICE_ID}")
    print(f"💻 Connecting to {SERVER_HOST}:{SERVER_PORT}")
    
    while True:
        # Connect to server
        socket_conn = connect_to_server()
        if not socket_conn:
            print("⏳ Retrying in 5 seconds...")
            time.sleep(5)
            continue
        
        try:
            # Send data every 5 seconds
            while True:
                if not send_status_data(socket_conn):
                    break
                time.sleep(5)
                
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
