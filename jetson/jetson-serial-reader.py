# Read data from Arduino via serial connection

import serial

def read_serial_data(port='/dev/ttyUSB0', baudrate=9600):
    ser = serial.Serial(port, baudrate)
    while True:
        data = ser.readline().decode('utf-8').strip()  # Read serial data
        print(f"Received: {data}")
        # Perform computations here if needed
        send_to_server(data)

def send_to_server(data):
    # Call the socket server to send data to the web server
    pass
