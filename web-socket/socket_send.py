# ws_client.py
import asyncio
import websockets

HOST = "10.42.0.117"  # replace with your server IP
PORT = 65431

async def send_message():
    uri = f"ws://{HOST}:{PORT}"   # use wss:// if the server uses TLS
    try:
        async with websockets.connect(uri) as websocket:
            await websocket.send("hello")
            print("Sent: hello")
            # optionally wait for a reply
            reply = await websocket.recv()
            print("Received from server:", reply)
    except Exception as e:
        print("WebSocket error:", e)

if __name__ == "__main__":
        asyncio.run(send_message())
