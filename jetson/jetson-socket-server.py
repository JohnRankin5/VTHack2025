# Socket server to send data to web server
import socket

HOST = "192.168.1.30"  # Web server IP
PORT = 5000             # Port to communicate with the web server

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def send_to_webserver(data):
    try:
        s.sendall(data.encode())  # Send data to web server
    except Exception as e:
        print(f"Error sending data: {e}")

# Example function call after computation
send_to_webserver("processed data from Jetson")
