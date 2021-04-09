"""This module is used to listen on a port to receive a message to write to the broker."""
import socket
import json
from event_logger import get_logger
from mqtt_writer import publish_to_mqtt
from config import get_settings

MESSAGE_STATUS_SUCCESSFUL = "HTTP/1.1 200 OK"
MESSAGE_STATUS_UNSUCCESSFUL = "HTTP/1.1 404 Not Found"
INCORRECT_FORMAT_TITLE = "Incorrect format of the received file: %s"

event_log = get_logger("__listener__")


class SocketConnectionError(Exception):
    """Common class for socket connection errors"""


class SocketConnection:
    """Context manager for connect to socket"""

    def __init__(self, settings):
        self.host = settings.get("host")
        self.port = settings.get("port")
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __enter__(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
        except PermissionError as err:
            raise SocketConnectionError from err
        except socket.gaierror as err:
            raise SocketConnectionError from err

        self.server_socket.listen()
        return self.server_socket

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server_socket.close()


def start_listening() -> None:
    """listen on a port to receive a message. Received message must be a dictionary"""
    event_log.info("Start working")

    settings_to_socket = get_settings("settings_to_socket")
    settings_to_publish = get_settings("settings_to_publish")

    try:
        with SocketConnection(settings_to_socket) as server_socket:
            while True:
                event_log.debug("Wait connection...")

                conn, _ = server_socket.accept()
                request = conn.recv(1024).decode("utf-8")

                try:
                    received_message = json.loads(request)
                except json.decoder.JSONDecodeError as err:
                    event_log.error(INCORRECT_FORMAT_TITLE, str(err))

                if received_message.get("topic") and received_message.get("message"):
                    report = received_message.get("topic"), received_message.get("message")
                    successful = publish_to_mqtt(report, settings_to_publish)
                else:
                    err = "Does not contain a required field topic or message"
                    event_log.error(INCORRECT_FORMAT_TITLE, err)
                    successful = False

                response = MESSAGE_STATUS_SUCCESSFUL if successful else MESSAGE_STATUS_UNSUCCESSFUL
                conn.sendall(response.encode())
                conn.close()

    except SocketConnectionError as err:
        event_log.error("Socket connection error. Can't receive message. Reason: %s", str(err))

    event_log.info("End working")
