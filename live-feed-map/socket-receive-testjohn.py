import asyncio
import websockets

async def handler(websocket):
    async for message in websocket:
        print(f"Received: {message}")
    
async def main():
    async with websockets.serve(handler, '10.42.0.117', port=65431):
        print("server listening on 10.42.0.117:65431")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())