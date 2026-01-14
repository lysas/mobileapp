import socket
import sys

def check_port(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    sock.close()
    return result == 0

if check_port(8000):
    print("PORT_8000_OPEN")
else:
    print("PORT_8000_CLOSED")
