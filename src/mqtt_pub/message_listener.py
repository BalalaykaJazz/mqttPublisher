"""This module is used to listen on a port to receive a message to write to the broker."""
import socket
import ssl
import json
from .user_auth import client_authenticate, get_salt_from_hash  # pylint: disable = import-error
from .event_logger import get_info_logger, get_error_logger  # pylint: disable = import-error
from .mqtt_writer import read_from_mqtt  # pylint: disable = import-error
from .config import get_settings_to_socket, get_settings_to_publish  # pylint: disable = import-error

MESSAGE_STATUS_SUCCESSFUL = "OK"
INCORRECT_FORMAT_TITLE = "Incorrect format of the received file: %s"
SLEEP_DURATION_AFTER_SENDING = 3
AUTHENTICATION_CHECK = "/check_auth"
CLIENT_WAITING_ANSWER = "/in/params"
COUNT_OF_CHAR = len(CLIENT_WAITING_ANSWER)
TOPIC_WITH_ANSWERS = "/out/info"

event_log = get_info_logger("INFO__listener__")
error_log = get_error_logger("ERR__listener__")


class SocketConnectionError(Exception):
    """Исключение для ошибок при подключении к сокету"""


class SocketConnection:
    """Менеджер контекста для подключения к сокету"""

    def __init__(self, settings):
        self.host = settings.get("socket_host")
        self.port = settings.get("socket_port")

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if settings.get("use_ssl"):
            self.server_socket = ssl.wrap_socket(self.server_socket,  # pylint: disable = deprecated-method
                                                 keyfile=settings.get("ssl_keyfile_path"),
                                                 certfile=settings.get("ssl_certfile_path"),
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
    """Сообщение должно содержать обязательные поля."""

    if received_message.get("message") == "/get_salt" \
            and received_message.get("user"):
        return True

    if received_message.get("message") == "/check_auth" \
            and received_message.get("user")\
            and received_message.get("password"):
        return True

    return sorted(list(received_message.keys())) == ["message", "password", "topic", "user"]


def execute_action(message: dict) -> str:
    """
    Выполнение действия указанного в поле action.

    Возвращаемое значение: строка с результатом действия
    """

    action = message.get("message")

    if action == "/get_salt":
        return get_salt_from_hash(message["user"])

    if action == "/check_auth":
        result = check_authorization(message)
        if result:
            event_log.info("login user %s : %s", message.get("user"), result)
        return result

    return f"Неизвестное действие: {action}"


def check_authorization(message: dict) -> str:
    """
    Проверяется правильность логина и пароля, который ввел пользователь.

    Возвращаемое значение: строка с результатом проверки.
    """

    if message.get("user") is None or message.get("password") is None:
        raise KeyError

    result = client_authenticate(message["user"],
                                 message["password"])

    return MESSAGE_STATUS_SUCCESSFUL if result else "Неизвестное имя пользователя или пароль"


def message_handling(request: str, settings_to_publish: dict) -> str:
    """
    Проверяет входящее сообщение и публикует в брокере mqtt.
    Если сообщение подразумевает ответ от брокера
    (топик соответствует формату CLIENT_WAITING_ANSWER),
    То подписывается на топик TOPIC_WITH_ANSWERS

    Результат операции возвращается клиенту.
    """

    # Сообщение должно быть в формате JSON
    try:
        received_message = json.loads(request)
    except json.decoder.JSONDecodeError as err:
        event_log.error(INCORRECT_FORMAT_TITLE, str(err))
        return "Неправильный формат сообщения"

    # Сообщение дожно иметь необходимые поля
    if not is_correct_format_message(received_message):
        answer_for_client = "Сообщение не содержит необходимые поля"
        event_log.error(INCORRECT_FORMAT_TITLE, answer_for_client)
        return answer_for_client

    # Выполнение служебный действий
    if received_message.get("message") == "/get_salt" or\
            received_message.get("message") == "/check_auth":
        return execute_action(received_message)

    # Проверка авторизации пользователя (при каждом сообщении)
    answer_for_client = check_authorization(received_message)
    if answer_for_client != MESSAGE_STATUS_SUCCESSFUL:
        event_log.error(answer_for_client)
        return answer_for_client

    report = received_message.get("topic"), received_message.get("message")

    if report[0][-COUNT_OF_CHAR:] == CLIENT_WAITING_ANSWER:
        # Получение ответа от устройства
        topic_with_answer = report[0][:-COUNT_OF_CHAR] + TOPIC_WITH_ANSWERS
        return read_from_mqtt(settings=settings_to_publish,
                              topic_for_read=topic_with_answer,
                              topic_for_write=report[0],
                              message=report[1])

    return MESSAGE_STATUS_SUCCESSFUL


def open_socket(settings_to_socket: dict, settings_to_publish: dict):
    """
    Прослушивает порт и получает сообщение
    """

    try:
        with SocketConnection(settings_to_socket) as server_socket:

            while True:
                conn, _ = server_socket.accept()
                request = conn.recv(1024).decode("utf-8")

                response = message_handling(request, settings_to_publish)

                conn.sendall(response.encode())
                conn.close()

    except SocketConnectionError as err:
        event_log.error("Ошибка подключения к сокету."
                        " Не удалось получить сообщение по причине: %s", str(err))
    except socket.timeout:
        open_socket(settings_to_socket, settings_to_publish)
    except KeyboardInterrupt:
        event_log.info("Ручная остановка программы")


def start_listening():
    """Получение настроек и открытие сокета"""

    settings_to_socket = get_settings_to_socket()
    settings_to_publish = get_settings_to_publish()

    event_log.info("Начало работы: %s:%s",
                   settings_to_socket.get("socket_host"),
                   settings_to_socket.get("socket_port"))

    open_socket(settings_to_socket, settings_to_publish)

    event_log.info("Завершение работы")
