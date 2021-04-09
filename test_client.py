"""
This program for test sending a message to message_listener
"""
import socket
import sys
from config import get_settings

settings_to_socket = get_settings("settings_to_socket")
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server_socket.connect((settings_to_socket.get("host"), settings_to_socket.get("port")))
except ConnectionRefusedError:
    print("Server is not running")
    sys.exit(1)

# data = input('write to server: ')
MESSAGE = '{"topic": "/balalaykajazz/out/setup", "message": "turn on"}'

if MESSAGE:
    # Send message
    server_socket.send(MESSAGE.encode())

    # Get answer
    answer = server_socket.recv(1024)
    print(answer.decode())

# End program
server_socket.close()
