import asyncio
import websockets
import json

WS_URI = "ws://localhost:8765"  # Point to your server

async def receive_lidar_data():
    try:
        async with websockets.connect(WS_URI) as websocket:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print("Client received:", data)
    except Exception as e:
        print(f"Error in client connection: {e}")

asyncio.run(receive_lidar_data())
