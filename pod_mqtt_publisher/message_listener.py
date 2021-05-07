"""This module is used to listen on a port to receive a message to write to the broker."""
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, gaierror
import ssl
import json
import time
from user_auth import client_authenticate
from event_logger import get_logger  # type: ignore
from mqtt_writer import publish_to_mqtt  # type: ignore
from config import get_settings  # type: ignore

MESSAGE_STATUS_SUCCESSFUL = "HTTP/1.1 200 OK"
MESSAGE_STATUS_UNSUCCESSFUL = "HTTP/1.1 404 Not Found"
INCORRECT_FORMAT_TITLE = "Incorrect format of the received file: %s"
SLEEP_DURATION_AFTER_SENDING = 3

event_log = get_logger("__listener__")


class SocketConnectionError(Exception):
    """Common class for socket connection errors"""


class SocketConnection:
    """Context manager for connect to socket"""

    def __init__(self, settings):
        self.host = settings.get("host")
        self.port = settings.get("port")

        self.server_socket = socket(AF_INET, SOCK_STREAM)

        if settings.get("use_ssl"):
            self.server_socket = ssl.wrap_socket(self.server_socket,
                                                 keyfile=settings.get("SSL_KEYFILE_PATH"),
                                                 certfile=settings.get("SSL_CERTFILE_PATH"),
                                                 server_side=True)

    def __enter__(self):
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
        except PermissionError as err:
            raise SocketConnectionError from err
        except gaierror as err:
            raise SocketConnectionError from err

        self.server_socket.listen(1)
        return self.server_socket

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server_socket.close()


def is_correct_format_message(received_message: dict) -> bool:
    """The message must contain the required fields"""

    return list(received_message.keys()) == ["topic", "message", "user", "password"]


def start_listening() -> None:
    """listen on a port to receive a message. Received message must be a dictionary"""

    settings_to_socket = get_settings("settings_to_socket")
    settings_to_publish = get_settings("settings_to_publish")

    event_log.info("Start working on %s:%s",
                   settings_to_socket.get("host"),
                   settings_to_socket.get("port"))

    try:
        with SocketConnection(settings_to_socket) as server_socket:
            while True:

                conn, _ = server_socket.accept()
                request = conn.recv(1024).decode("utf-8")

                try:
                    received_message = json.loads(request)
                except json.decoder.JSONDecodeError as err:
                    event_log.error(INCORRECT_FORMAT_TITLE, str(err))

                if not is_correct_format_message(received_message):
                    err_str = "Does not contain a required field"
                    event_log.error(INCORRECT_FORMAT_TITLE, err_str)
                    successful = False
                elif not client_authenticate(received_message.get("user"),
                                             received_message.get("password")):
                    err_str = "Unknown username or password"
                    event_log.error(err_str)
                    successful = False
                else:
                    report = received_message.get("topic"), received_message.get("message")
                    successful = publish_to_mqtt(report, settings_to_publish)

                response = MESSAGE_STATUS_SUCCESSFUL if successful else MESSAGE_STATUS_UNSUCCESSFUL
                conn.sendall(response.encode())
                conn.close()
                time.sleep(SLEEP_DURATION_AFTER_SENDING)

    except SocketConnectionError as err:
        event_log.error("Socket connection error. Can't receive message. Reason: %s", str(err))

    event_log.info("End working")
