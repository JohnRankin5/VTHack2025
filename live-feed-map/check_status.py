#!/usr/bin/env python3
"""
Check the status of all services for the Mac Camera Live Feed Map
"""

import requests
import asyncio
import websockets
import json

def check_nextjs_server():
    """Check if Next.js server is running"""
    try:
        response = requests.get("http://localhost:3000", timeout=2)
        if response.status_code == 200:
            print("✅ Next.js server is running on http://localhost:3000")
            return True
        else:
            print(f"⚠️  Next.js server responded with status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Next.js server is not running: {e}")
        return False

async def check_websocket_server():
    """Check if WebSocket video stream server is running"""
    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            print("✅ Video stream WebSocket server is running on ws://localhost:8765")
            
            # Try to receive one message to verify it's working
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(message)
                if data.get("type") == "frame":
                    detections = len(data.get('detections', []))
                    gestures = len(data.get('gestures', []))
                    print(f"📹 Video stream is active - detecting {detections} objects and {gestures} gestures")
                    return True
                else:
                    print(f"⚠️  Received unexpected message type: {data.get('type')}")
                    return False
            except asyncio.TimeoutError:
                print("⚠️  WebSocket connected but no frame data received")
                return False
                
    except ConnectionRefusedError:
        print("❌ Video stream WebSocket server is not running")
        return False
    except Exception as e:
        print(f"❌ WebSocket server error: {e}")
        return False

def check_camera_permissions():
    """Check if camera is accessible"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("❌ Camera could not be opened - check permissions")
            return False
        
        ret, frame = cap.read()
        cap.release()
        
        if ret and frame is not None:
            print("✅ Camera is accessible and working")
            return True
        else:
            print("❌ Camera is not working properly")
            return False
            
    except ImportError:
        print("❌ OpenCV not installed")
        return False
    except Exception as e:
        print(f"❌ Camera check failed: {e}")
        return False

async def main():
    """Check all services"""
    print("🚒 Mac Camera Live Feed Map - Status Check")
    print("=" * 50)
    
    # Check Next.js server
    nextjs_ok = check_nextjs_server()
    
    # Check WebSocket server
    websocket_ok = await check_websocket_server()
    
    # Check camera
    camera_ok = check_camera_permissions()
    
    print("\n" + "=" * 50)
    
    if nextjs_ok and websocket_ok and camera_ok:
        print("🎉 ALL SYSTEMS GO!")
        print("\n📋 Ready to use:")
        print("   1. Open: http://localhost:3000/live-feed")
        print("   2. Select: 'Firefighter Alpha (Mac Camera)'")
        print("   3. Click: 'Start Detection'")
        print("\n🎥 You should see your live camera feed with object detection!")
    else:
        print("⚠️  Some services need attention:")
        if not nextjs_ok:
            print("   - Start Next.js server: npm run dev")
        if not websocket_ok:
            print("   - Start video stream: ./start_mac_detector.sh")
        if not camera_ok:
            print("   - Check camera permissions in System Preferences")

if __name__ == "__main__":
    asyncio.run(main())
