#!/usr/bin/env python3
"""
Simple TCP client to test the socket server
"""
import socket
import json
import time

def test_connection():
    """Test TCP connection"""
    HOST = '10.42.0.117'
    PORT = 65431
    
    try:
        # Connect to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        print(f"✅ Connected to {HOST}:{PORT}")
        
        # Send test messages
        messages = [
            "Hello from test client!",
            json.dumps({"device_id": "TEST_001", "timestamp": time.time(), "message": "JSON test"}),
            "Another raw message",
            json.dumps({"device_type": "jetson", "status": "testing", "data": [1, 2, 3]})
        ]
        
        for i, message in enumerate(messages, 1):
            client_socket.send(message.encode('utf-8'))
            print(f"📡 Sent message {i}: {message}")
            time.sleep(1)
        
        client_socket.close()
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Connection error: {e}")

if __name__ == "__main__":
    test_connection()

