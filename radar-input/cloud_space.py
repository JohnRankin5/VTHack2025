from rplidarc1 import RPLidar
import asyncio

lidar = RPLidar("COM5", 460800)

async def process_scan_data():
    # Start the scan with dictionary output
    async with asyncio.TaskGroup() as tg:
        # Start the scan with dictionary output
        tg.create_task(lidar.simple_scan(make_return_dict=True))
        
        # Start the data processing task
        tg.create_task(process_queue(lidar.output_queue))
    
    # No need to return anything, the process runs indefinitely
    print("Lidar scanning started. Press Ctrl+C to stop.")
    
async def process_queue(queue):
    # This loop will run indefinitely, processing and printing the data
    while True:
        if not queue.empty():
            data = await queue.get()
            # Process and print the data
            print(f"Angle: {data['a_deg']}°, Distance: {data['d_mm']}mm, Quality: {data['q']}")
        else:
            await asyncio.sleep(0.1)  # Avoid overloading the CPU if there's no data

# Run the scan and continuous data processing
try:
    asyncio.run(process_scan_data())
except KeyboardInterrupt:
    lidar.reset()
    print("Lidar scan stopped.")
