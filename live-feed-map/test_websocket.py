#!/usr/bin/env python3
"""
Test WebSocket connection to video stream server
"""

import asyncio
import websockets
import json

async def test_websocket():
    """Test WebSocket connection"""
    try:
        print("🔌 Testing WebSocket connection...")
        
        async with websockets.connect("ws://localhost:8765") as websocket:
            print("✅ Connected to WebSocket server")
            
            # Wait for a few messages
            message_count = 0
            while message_count < 3:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    
                    if data.get("type") == "frame":
                        print(f"📹 Received frame message - detections: {len(data.get('detections', []))}")
                        message_count += 1
                    else:
                        print(f"📨 Received message: {data.get('type', 'unknown')}")
                        
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for message")
                    break
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
            
            print("✅ WebSocket test completed successfully")
            
    except ConnectionRefusedError:
        print("❌ Could not connect to WebSocket server")
        print("   Make sure the video stream server is running:")
        print("   python video_stream_server.py")
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
