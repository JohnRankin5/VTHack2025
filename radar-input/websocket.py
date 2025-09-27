import asyncio
import websockets
import json

async def receive_lidar_data():
    uri = "ws://localhost:8765"  # Connect to the WebSocket server running on the same laptop
    try:
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                data = json.loads(message)
                print(f"Received Lidar Data: {data}")
    except Exception as e:
        print(f"Error in client connection: {e}")

asyncio.run(receive_lidar_data())
