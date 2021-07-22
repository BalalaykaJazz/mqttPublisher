"""
This program for test sending a message to message_listener
"""
import socket
import sys
from src.pod_mqtt_publisher import settings  # pylint: disable = import-error

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    server_socket.connect((settings.socket_host, settings.socket_port))
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
