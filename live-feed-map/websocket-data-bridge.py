#!/usr/bin/env python3
"""
WebSocket Data Bridge - Combines WebSocket receiving with threaded data storage and Next.js API
"""

import asyncio
import websockets
import threading
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ThreadSafeDataStore:
    """Thread-safe storage for sensor data from WebSocket connections"""
    def __init__(self):
        self.data = []
        self.lock = threading.Lock()
        self.max_entries = 100  # Keep last 100 entries
    
    def add_data(self, raw_data, processed_data=None, device_type="unknown", source_port=None):
        """Add new sensor data entry"""
        with self.lock:
            entry = {
                'id': len(self.data) + 1,
                'timestamp': datetime.now().isoformat(),
                'raw_data': raw_data,
                'processed_data': processed_data,
                'device_type': device_type,
                'source_port': source_port,
                'source': 'websocket'
            }
            self.data.append(entry)
            if len(self.data) > self.max_entries:
                self.data = self.data[-self.max_entries:]
            logger.info(f"📊 Stored data from {device_type}: {len(self.data)} total entries")
    
    def get_latest(self, count=10):
        with self.lock:
            return self.data[-count:] if self.data else []
    
    def get_all(self):
        with self.lock:
            return self.data.copy()
    
    def get_stats(self):
        with self.lock:
            if not self.data:
                return {'total_entries': 0, 'latest_timestamp': None}
            device_counts = {}
            for entry in self.data:
                device_type = entry.get('device_type', 'unknown')
                device_counts[device_type] = device_counts.get(device_type, 0) + 1
            return {
                'total_entries': len(self.data),
                'latest_timestamp': self.data[-1]['timestamp'],
                'oldest_timestamp': self.data[0]['timestamp'],
                'device_breakdown': device_counts
            }

# Global data store
data_store = ThreadSafeDataStore()
async def make_handler(device_type, port):
    """Create a WebSocket handler for a specific device type (compat with websockets 8/9/10+)"""
    async def handler(websocket, path=None):  # <-- path is optional now
        client_ip = (websocket.remote_address[0] if websocket.remote_address else "?")
        logger.info(f"🔌 [{device_type.upper()}] Client connected from {client_ip}")
        try:
            async for message in websocket:
                # ----- Binary frames -----
                if isinstance(message, (bytes, bytearray)):
                    processed_data = {
                        'device_type': device_type,
                        'source_port': port,
                        'client_ip': client_ip,
                        'encoding': 'binary',
                        'binary_len': len(message)
                    }
                    data_store.add_data(
                        raw_data=f"<{len(message)} bytes>",
                        processed_data=processed_data,
                        device_type=device_type,
                        source_port=port
                    )
                    logger.info(f"📡 [{device_type.upper()}] {client_ip} -> <{len(message)} bytes>")
                    continue

                # ----- Text frames (JSON / plain) -----
                log_preview = message if len(message) <= 200 else (message[:200] + "...[truncated]")
                logger.info(f"📡 [{device_type.upper()}] {client_ip} -> {log_preview}")
                try:
                    if message and (message[0] in "{["):
                        processed_data = json.loads(message)
                        if isinstance(processed_data, dict):
                            processed_data.setdefault('device_type', device_type)
                            processed_data.setdefault('source_port', port)
                            processed_data.setdefault('client_ip', client_ip)
                    else:
                        processed_data = {
                            'raw_message': message,
                            'device_type': device_type,
                            'source_port': port,
                            'client_ip': client_ip
                        }

                    data_store.add_data(
                        raw_data=message,
                        processed_data=processed_data,
                        device_type=device_type,
                        source_port=port
                    )

                except json.JSONDecodeError as e:
                    logger.warning(f"⚠️ [{device_type.upper()}] JSON decode error: {e}")
                    data_store.add_data(
                        raw_data=message,
                        processed_data={'raw_message': message, 'device_type': device_type},
                        device_type=device_type,
                        source_port=port
                    )
                except Exception as e:
                    logger.error(f"❌ [{device_type.upper()}] Processing error: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 [{device_type.upper()}] Client {client_ip} disconnected")
        except Exception as e:
            logger.error(f"❌ [{device_type.upper()}] Handler error: {e}")
    return handler


class APIHandler(BaseHTTPRequestHandler):
    """HTTP API handler for Next.js integration"""
    def do_GET(self):
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
            elif path == '/api/device-data':
                self.handle_device_data(query_params)
            else:
                self.send_error(404, "Not Found")
        except Exception as e:
            logger.error(f"API error: {e}")
            self.send_error(500, "Internal Server Error")

    def send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def handle_sensor_data(self, query_params):
        count = int(query_params.get('count', ['10'])[0])
        data = data_store.get_latest(count)
        response = {'success': True, 'data': data, 'count': len(data)}
        self.send_response(200); self.send_header('Content-Type', 'application/json')
        self.send_cors_headers(); self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_device_data(self, query_params):
        device_type = query_params.get('device_type', ['all'])[0]
        count = int(query_params.get('count', ['10'])[0])
        all_data = data_store.get_latest(100)
        if device_type != 'all':
            filtered_data = [e for e in all_data if e.get('device_type') == device_type]
        else:
            filtered_data = all_data
        filtered_data = filtered_data[-count:] if filtered_data else []
        response = {'success': True, 'data': filtered_data, 'count': len(filtered_data), 'device_type': device_type}
        self.send_response(200); self.send_header('Content-Type', 'application/json')
        self.send_cors_headers(); self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_sensor_stats(self):
        stats = data_store.get_stats()
        response = {'success': True, 'stats': stats}
        self.send_response(200); self.send_header('Content-Type', 'application/json')
        self.send_cors_headers(); self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def handle_health(self):
        response = {
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'data_entries': len(data_store.get_all())
        }
        self.send_response(200); self.send_header('Content-Type', 'application/json')
        self.send_cors_headers(); self.end_headers()
        self.wfile.write(json.dumps(response).encode())

    def log_message(self, format, *args):
        logger.info(f"{self.address_string()} - {format % args}")

def start_api_server(host='localhost', port=5003):
    def run_server():
        try:
            server = HTTPServer((host, port), APIHandler)
            logger.info(f"🌐 API server listening on {host}:{port}")
            server.serve_forever()
        except Exception as e:
            logger.error(f"❌ Failed to start API server: {e}")
    api_thread = threading.Thread(target=run_server, daemon=True)
    api_thread.start()
    return api_thread

async def main():
    # Configuration
    laptop_port = 65431
    jetson_port = 65432
    host = "10.42.0.117"  # change to "0.0.0.0" to bind all interfaces
    api_host = "localhost"
    api_port = 5003

    logger.info("🚀 Starting WebSocket Data Bridge...")

    # Start API server in background thread
    start_api_server(api_host, api_port)

    # Create WebSocket handlers
    laptop_handler = await make_handler("laptop", laptop_port)
    jetson_handler = await make_handler("jetson", jetson_port)

    # Start WebSocket servers (no message size limit)
    await websockets.serve(laptop_handler, host, laptop_port, max_size=None)
    await websockets.serve(jetson_handler, host, jetson_port, max_size=None)

    logger.info(f"🔌 WebSocket servers listening:")
    logger.info(f"   📱 LAPTOP: ws://{host}:{laptop_port}")
    logger.info(f"   🤖 JETSON: ws://{host}:{jetson_port}")
    logger.info(f"🌐 API endpoints available:")
    logger.info(f"   📊 Data:  http://{api_host}:{api_port}/api/sensor-data")
    logger.info(f"   📈 Stats: http://{api_host}:{api_port}/api/sensor-stats")
    logger.info(f"   🏥 Health: http://{api_host}:{api_port}/api/health")
    logger.info(f"   🔍 Device Data: http://{api_host}:{api_port}/api/device-data?device_type=laptop")

    await asyncio.Future()  # keep running

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down WebSocket Data Bridge...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
