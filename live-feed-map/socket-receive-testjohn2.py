import asyncio
import websockets

async def make_handler(tag):
    async def handler(websocket):
        async for message in websocket:
            print(f"[{tag}] {websocket.remote_address[0]} -> {message}")
    return handler

async def main():
    laptop_port = 65431
    jetson_port = 65432
    host = "10.42.0.117"  # change to "0.0.0.0" if you want to bind all interfaces

    laptop_server = await websockets.serve(await make_handler("LAPTOP"), host, laptop_port)
    jetson_server = await websockets.serve(await make_handler("JETSON"), host, jetson_port)

    print(f"listening on ws://{host}:{laptop_port} (LAPTOP) and ws://{host}:{jetson_port} (JETSON)")
    await asyncio.Future()  # keep running

if __name__ == "__main__":
    asyncio.run(main())
