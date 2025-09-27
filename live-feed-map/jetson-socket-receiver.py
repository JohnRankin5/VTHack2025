#!/usr/bin/env python3
"""
Jetson Socket Receiver
Receives sensor data from Jetson via socket and provides HTTP API for Next.js
"""

import socket
import threading
import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SensorDataStore:
    """Thread-safe storage for sensor data"""
    def __init__(self):
        self.data = []
        self.lock = threading.Lock()
        self.max_entries = 100  # Keep last 100 entries
    
    def add_data(self, raw_data, processed_data=None):
        """Add new sensor data entry"""
        with self.lock:
            entry = {
                'id': len(self.data) + 1,
                'timestamp': datetime.now().isoformat(),
                'raw_data': raw_data,
                'processed_data': processed_data,
                'source': 'jetson'
            }
            self.data.append(entry)
            
            # Keep only the most recent entries
            if len(self.data) > self.max_entries:
                self.data = self.data[-self.max_entries:]
    
    def get_latest(self, count=10):
        """Get latest sensor data entries"""
        with self.lock:
            return self.data[-count:] if self.data else []
    
    def get_all(self):
        """Get all sensor data"""
        with self.lock:
            return self.data.copy()
    
    def get_stats(self):
        """Get basic statistics"""
        with self.lock:
            if not self.data:
                return {'total_entries': 0, 'latest_timestamp': None}
            
            return {
                'total_entries': len(self.data),
                'latest_timestamp': self.data[-1]['timestamp'],
                'oldest_timestamp': self.data[0]['timestamp']
            }

# Global data store
sensor_store = SensorDataStore()

class SocketServer:
    """Socket server to receive data from Jetson"""
    
    def __init__(self, host='0.0.0.0', port=5000):
        self.host = host
        self.port = port
        self.running = False
        self.server_socket = None
    
    def start(self):
        """Start the socket server"""
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.running = True
            
            logger.info(f"Socket server listening on {self.host}:{self.port}")
            
            while self.running:
                try:
                    client_socket, address = self.server_socket.accept()
                    logger.info(f"Connection from {address}")
                    
                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self.handle_client,
                        args=(client_socket, address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                except socket.error as e:
                    if self.running:
                        logger.error(f"Socket error: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Failed to start socket server: {e}")
        finally:
            self.stop()
    
    def handle_client(self, client_socket, address):
        """Handle individual client connection"""
        try:
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    break
                
                # Decode and process the data
                raw_data = data.decode('utf-8').strip()
                logger.info(f"Received from {address}: {raw_data}")
                
                # Try to parse as JSON, fallback to raw string
                try:
                    processed_data = json.loads(raw_data)
                except json.JSONDecodeError:
                    processed_data = raw_data
                
                # Store the data
                sensor_store.add_data(raw_data, processed_data)
                
        except Exception as e:
            logger.error(f"Error handling client {address}: {e}")
        finally:
            client_socket.close()
            logger.info(f"Client {address} disconnected")
    
    def stop(self):
        """Stop the socket server"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
        logger.info("Socket server stopped")

class APIHandler(BaseHTTPRequestHandler):
    """HTTP API handler for Next.js integration"""
    
    def do_GET(self):
        """Handle GET requests from Next.js"""
        try:
            parsed_path = urlparse(self.path)
            path = parsed_path.path
            query_params = parse_qs(parsed_path.query)
            
            # Set CORS headers
            self.send_cors_headers()
            
            if path == '/api/sensor-data':
                self.handle_sensor_data(query_params)
            elif path == '/api/sensor-stats':
                self.handle_sensor_stats()
            elif path == '/api/health':
                self.handle_health()
            else:
                self.send_error(404, "Not Found")
                
        except Exception as e:
            logger.error(f"API error: {e}")
            self.send_error(500, "Internal Server Error")
    
    def send_cors_headers(self):
        """Send CORS headers for Next.js integration"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def handle_sensor_data(self, query_params):
        """Handle sensor data requests"""
        count = int(query_params.get('count', ['10'])[0])
        data = sensor_store.get_latest(count)
        
        response = {
            'success': True,
            'data': data,
            'count': len(data)
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_sensor_stats(self):
        """Handle sensor statistics requests"""
        stats = sensor_store.get_stats()
        response = {
            'success': True,
            'stats': stats
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def handle_health(self):
        """Handle health check requests"""
        response = {
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.info(f"{self.address_string()} - {format % args}")

class APIServer:
    """HTTP API server for Next.js integration"""
    
    def __init__(self, host='localhost', port=5001):
        self.host = host
        self.port = port
        self.server = None
    
    def start(self):
        """Start the API server"""
        try:
            self.server = HTTPServer((self.host, self.port), APIHandler)
            logger.info(f"API server listening on {self.host}:{self.port}")
            self.server.serve_forever()
        except Exception as e:
            logger.error(f"Failed to start API server: {e}")
    
    def stop(self):
        """Stop the API server"""
        if self.server:
            self.server.shutdown()
        logger.info("API server stopped")

def main():
    """Main function to start both servers"""
    logger.info("Starting Jetson Socket Receiver...")
    
    # Start socket server in a separate thread
    socket_server = SocketServer(host='0.0.0.0', port=5000)
    socket_thread = threading.Thread(target=socket_server.start)
    socket_thread.daemon = True
    socket_thread.start()
    
    # Start API server in the main thread
    api_server = APIServer(host='localhost', port=5001)
    
    try:
        api_server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        socket_server.stop()
        api_server.stop()

if __name__ == "__main__":
    main()
