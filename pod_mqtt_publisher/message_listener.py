"""This module is used to listen on a port to receive a message to write to the broker."""
import socket
import ssl
import json
import time
from user_auth import client_authenticate
from event_logger import get_logger  # type: ignore
from mqtt_writer import publish_to_mqtt, read_from_mqtt  # type: ignore
from config import get_settings  # type: ignore

MESSAGE_STATUS_SUCCESSFUL = "OK"
INCORRECT_FORMAT_TITLE = "Incorrect format of the received file: %s"
SLEEP_DURATION_AFTER_SENDING = 3
AUTHENTICATION_CHECK = "/check_auth"
CLIENT_WAITING_ANSWER = "/in/params"
COUNT_OF_CHAR = len(CLIENT_WAITING_ANSWER)
TOPIC_WITH_ANSWERS = "/out/info"

event_log = get_logger("__listener__")


class SocketConnectionError(Exception):
    """Common class for socket connection errors"""


class SocketConnection:
    """Context manager for connect to socket"""

    def __init__(self, settings):
        self.host = settings.get("host")
        self.port = settings.get("port")

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if settings.get("use_ssl"):
            self.server_socket = ssl.wrap_socket(self.server_socket,
                                                 keyfile=settings.get("SSL_KEYFILE_PATH"),
                                                 certfile=settings.get("SSL_CERTFILE_PATH"),
                                                 server_side=True)

    def __enter__(self):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((self.host, self.port))
        except PermissionError as err:
            raise SocketConnectionError from err
        except socket.gaierror as err:
            raise SocketConnectionError from err

        self.server_socket.listen(1)
        return self.server_socket

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.server_socket.close()


def is_correct_format_message(received_message: dict) -> bool:
    """The message must contain the required fields"""

    return sorted(list(received_message.keys())) == ["message", "password", "topic", "user"]


def message_handling(request: str, settings_to_publish: dict) -> str:
    """
    Checking incoming message and publish to mqtt.
    If topic contains CLIENT_WAITING_ANSWER we subscribe to TOPIC_WITH_ANSWERS

    Operation's result is returned to client.
    """

    try:
        received_message = json.loads(request)
    except json.decoder.JSONDecodeError as err:
        event_log.error(INCORRECT_FORMAT_TITLE, str(err))
        return "Message wrong format"

    if not is_correct_format_message(received_message):
        answer_for_client = "The message does not contain a required field"
        event_log.error(INCORRECT_FORMAT_TITLE, answer_for_client)
        return answer_for_client

    if not client_authenticate(received_message.get("user"),
                               received_message.get("password")):
        answer_for_client = "Unknown username or password"
        event_log.error(answer_for_client)
        return answer_for_client

    report = received_message.get("topic"), received_message.get("message")
    if report[1] == AUTHENTICATION_CHECK:
        event_log.info("login user: %s", received_message.get("user"))
        return MESSAGE_STATUS_SUCCESSFUL

    successful = publish_to_mqtt(report, settings_to_publish)

    if successful and report[0][-COUNT_OF_CHAR:] == CLIENT_WAITING_ANSWER:
        # get answer from device
        topic_with_answer = report[0][:-COUNT_OF_CHAR] + TOPIC_WITH_ANSWERS
        return read_from_mqtt(settings=settings_to_publish,
                              topic=topic_with_answer)

    return MESSAGE_STATUS_SUCCESSFUL if successful else "Can't publish message."


def open_socket(settings_to_socket: dict, settings_to_publish: dict) -> None:
    """
    listen on a port to receive a message. Received message must be a dictionary
    """

    try:
        with SocketConnection(settings_to_socket) as server_socket:

            while True:
                conn, _ = server_socket.accept()
                request = conn.recv(1024).decode("utf-8")

                response = message_handling(request, settings_to_publish)

                conn.sendall(response.encode())
                conn.close()
                time.sleep(SLEEP_DURATION_AFTER_SENDING)

    except SocketConnectionError as err:
        event_log.error("Socket connection error. Can't receive message. Reason: %s", str(err))
    except socket.timeout:
        open_socket(settings_to_socket, settings_to_publish)


def start_listening() -> None:
    """Get settings and open socket"""

    settings_to_socket = get_settings("settings_to_socket")
    settings_to_publish = get_settings("settings_to_publish")

    event_log.info("Start working on %s:%s",
                   settings_to_socket.get("host"),
                   settings_to_socket.get("port"))

    open_socket(settings_to_socket, settings_to_publish)

    event_log.info("End working")
