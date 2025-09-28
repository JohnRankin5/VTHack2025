#!/usr/bin/env python3
"""
TCP Socket Test - Compatible with jetson-socket-receiver.py
"""
import socket
import threading
import json
import time

def handle_client(client_socket, address):
    """Handle individual client connection"""
    print(f"✅ Client connected from {address}")
    try:
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            
            message = data.decode('utf-8').strip()
            print(f"📡 Received from {address}: {message}")
            
            # Try to parse as JSON
            try:
                json_data = json.loads(message)
                print(f"📊 Parsed JSON: {json_data}")
            except json.JSONDecodeError:
                print(f"📄 Raw message: {message}")
                
    except Exception as e:
        print(f"❌ Error handling client {address}: {e}")
    finally:
        client_socket.close()
        print(f"🔌 Client {address} disconnected")

def main():
    """Main TCP socket server"""
    HOST = '10.42.0.117'
    PORT = 65431
    
    # Create TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server_socket.bind((HOST, PORT))
        server_socket.listen(5)
        print(f"🚀 TCP Server listening on {HOST}:{PORT}")
        print("Waiting for connections...")
        
        while True:
            client_socket, address = server_socket.accept()
            
            # Handle client in separate thread
            client_thread = threading.Thread(
                target=handle_client, 
                args=(client_socket, address)
            )
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down server...")
    except Exception as e:
        print(f"❌ Server error: {e}")
    finally:
        server_socket.close()
        print("✅ Server stopped")

if __name__ == "__main__":
    main()

