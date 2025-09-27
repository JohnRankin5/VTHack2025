import asyncio
import json
import websockets
from rplidarc1 import RPLidar

PORT = "COM3"       # Adjust to your COM port
BAUD = 460800       # Adjust to your lidar model
WS_PORT = 8765

lidar = RPLidar(PORT, BAUD)
clients = set()  # store connected clients

# Broadcast lidar points to all connected clients
async def process_queue(queue):
    while True:
        if not queue.empty():
            data = await queue.get()
            if data["d_mm"] is not None:
                payload = {
                    "angle": round(data["a_deg"], 2),
                    "distance": round(data["d_mm"], 1),
                    "quality": data["q"]
                }
                message = json.dumps(payload)

                if clients:
                    await asyncio.gather(*(c.send(message) for c in clients))

                # Print locally
                print("Server:", payload)
        else:
            await asyncio.sleep(0.01)

# Handle new WebSocket connections
async def ws_handler(websocket):
    clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        clients.remove(websocket)

# Main server loop
async def main():
    async with websockets.serve(ws_handler, "localhost", WS_PORT):
        print(f"Lidar WebSocket server running at ws://localhost:{WS_PORT}")
        async with asyncio.TaskGroup() as tg:
            tg.create_task(lidar.simple_scan(make_return_dict=True))
            tg.create_task(process_queue(lidar.output_queue))

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Stopping...")
    lidar.reset()
    lidar.disconnect()
