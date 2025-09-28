import asyncio
import serial
from rplidarc1 import RPLidar
from datetime import datetime
import csv
import os

# -------------------
# Serial Setup
# -------------------
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

# -------------------
# Lidar Setup
# -------------------
lidar = RPLidar("/dev/ttyUSB0", 460800)

async def read_serial():
    """Read a single line from the serial port asynchronously."""
    line = await asyncio.to_thread(ser.readline)
    if line:
        return line.decode("utf-8").strip()
    return None

async def process_queue(queue):
    """Yield lidar data from the queue."""
    while True:
        if not queue.empty():
            data = await queue.get()
            return data  # return one datapoint
        else:
            await asyncio.sleep(0.01)

# -------------------
# CSV Setup
# -------------------
CSV_FILE = "log.csv"
CSV_HEADERS = ["timestamp", "serial_data", "lidar_angle_deg", "lidar_distance_mm", "lidar_quality"]

# If the file doesn’t exist, create it and add headers
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)


# -------------------
# Combined Loop
# -------------------
async def main():
    async with asyncio.TaskGroup() as tg:
        # Start lidar scanning
        tg.create_task(lidar.simple_scan(make_return_dict=True))

        # Open CSV for appending
        with open(CSV_FILE, "a", newline="") as f:
            writer = csv.writer(f)

            while True:
                # Run both tasks concurrently
                serial_task = asyncio.create_task(read_serial())
                lidar_task = asyncio.create_task(process_queue(lidar.output_queue))

                serial_data, lidar_data = await asyncio.gather(serial_task, lidar_task)

                if serial_data and lidar_data:
                    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # HH:MM:SS.mmm

                    # Print to console
                    print(
                        f"[{timestamp}] Serial: {serial_data} | "
                        f"Lidar → Angle: {lidar_data['a_deg']}°, Distance: {lidar_data['d_mm']}mm, Quality: {lidar_data['q']}"
                    )

                    # Write one clean row to CSV
                    writer.writerow([
                        timestamp,
                        serial_data,  # stays in ONE column
                        lidar_data.get("a_deg", ""),
                        lidar_data.get("d_mm", ""),
                        lidar_data.get("q", ""),
                    ])
                    f.flush()  # ensure data is written immediately

# -------------------
# Run
# -------------------
try:
    asyncio.run(main())
except KeyboardInterrupt:
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nProgram interrupted. Closing resources...")
    lidar.reset()
    if ser.is_open:
        ser.close()
    print("Closed.")


