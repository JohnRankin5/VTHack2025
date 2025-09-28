#!/usr/bin/env python3
"""
Camera-Only System Launcher
Runs the enhanced video stream server with object detection, gesture detection, and radar HUD
(without requiring the WebSocket data bridge for radar data)
"""

import subprocess
import sys
import os
import time

def main():
    """Main function to start the camera system"""
    print("=" * 60)
    print("🔥 FIREGUARD CAMERA SYSTEM")
    print("=" * 60)
    print("📹 Starting camera with object detection + gesture detection")
    print("🎯 Radar HUD ready (will show when radar data available)")
    print("🚀 No network dependencies required")
    print("=" * 60)
    
    try:
        print("🚀 Starting Enhanced Video Stream Server...")
        
        # Run the video stream server directly
        subprocess.run([
            sys.executable, "video_stream_server.py"
        ], check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Video server failed: {e}")
    except KeyboardInterrupt:
        print("\n🛑 Shutting down camera system...")
    except Exception as e:
        print(f"❌ System error: {e}")
    finally:
        print("🔄 Camera system shutdown complete")

if __name__ == "__main__":
    # Check if we're in the right directory
    if not os.path.exists("video_stream_server.py"):
        print("❌ Error: video_stream_server.py not found in current directory")
        print("💡 Please run this script from the live-feed-map directory")
        sys.exit(1)
    
    print("💡 Usage:")
    print("   📹 Video Stream: ws://localhost:8765")
    print("   🔗 Next.js Frontend: http://localhost:3000")
    print("   🎮 Features: Object Detection + Gesture Recognition + Radar HUD")
    print("   ⚠️  Press Ctrl+C to stop")
    print()
    
    main()
