#!/usr/bin/env python3
"""
Integrated Radar + Video System Launcher
Starts both the websocket data bridge and the enhanced video stream server
"""

import subprocess
import threading
import time
import signal
import sys
import os

def run_websocket_bridge():
    """Run the websocket data bridge for radar data"""
    print("🚀 Starting WebSocket Data Bridge...")
    try:
        subprocess.run([
            sys.executable, "websocket-data-bridge.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ WebSocket bridge failed: {e}")
    except KeyboardInterrupt:
        print("🛑 WebSocket bridge interrupted")

def run_video_server():
    """Run the enhanced video stream server"""
    print("🚀 Starting Enhanced Video Stream Server...")
    # Wait a bit for websocket bridge to start
    time.sleep(3)
    try:
        subprocess.run([
            sys.executable, "video_stream_server.py"
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Video server failed: {e}")
    except KeyboardInterrupt:
        print("🛑 Video server interrupted")

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n🛑 Received signal {signum}, shutting down...")
    sys.exit(0)

def main():
    """Main function to start the integrated system"""
    print("=" * 60)
    print("🔥 FIREGUARD RADAR-INTEGRATED VIDEO SYSTEM")
    print("=" * 60)
    print("🔧 Starting integrated radar + video system...")
    print("📡 Radar data will be processed from WebSocket")
    print("📹 Video stream will include radar HUD overlay")
    print("=" * 60)
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create threads for both services
    websocket_thread = threading.Thread(target=run_websocket_bridge, daemon=True)
    video_thread = threading.Thread(target=run_video_server, daemon=True)
    
    try:
        # Start websocket bridge first
        websocket_thread.start()
        print("✅ WebSocket Data Bridge thread started")
        
        # Start video server
        video_thread.start() 
        print("✅ Video Stream Server thread started")
        
        print("\n🌐 System Ready! Access points:")
        print("   📊 WebSocket Data Bridge API: http://localhost:5003")
        print("   📹 Video Stream: ws://localhost:8765")
        print("   🔗 Next.js Frontend: http://localhost:3000")
        print("\n📡 Send radar data to: ws://10.42.0.117:65431")
        print("🤖 Send jetson data to: ws://10.42.0.117:65432")
        print("\n💡 Radar data format: {\"type\": \"radar_distance\", \"distance_m\": 5.5, \"t_sec\": 1234567890}")
        print("\n⚠️  Press Ctrl+C to stop all services")
        print("=" * 60)
        
        # Keep main thread alive
        while True:
            if not websocket_thread.is_alive():
                print("❌ WebSocket bridge thread died")
                break
            if not video_thread.is_alive():
                print("❌ Video server thread died")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down integrated system...")
    except Exception as e:
        print(f"❌ System error: {e}")
    finally:
        print("🔄 System shutdown complete")

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("websocket-data-bridge.py"):
        print("❌ Error: websocket-data-bridge.py not found in current directory")
        print("💡 Please run this script from the live-feed-map directory")
        sys.exit(1)
    
    if not os.path.exists("video_stream_server.py"):
        print("❌ Error: video_stream_server.py not found in current directory")
        print("💡 Please run this script from the live-feed-map directory")
        sys.exit(1)
    
    main()
