"""
Client authorization on the server
"""

import hmac
from pod_mqtt_publisher.config import get_settings


def client_authenticate(client_user: str, received_token_hash: str) -> bool:
    """
    Login and password verification.
    User must be specified in the system.
    The password received from the client must match the server password.
    """

    correct_token_hash = get_password_hash(client_user)

    if not correct_token_hash or not received_token_hash:
        return False

    return hmac.compare_digest(correct_token_hash, received_token_hash)


def get_password_hash(client_user: str) -> str:
    """
    Функция возвращает хэш пароля пользователя.
    Если пользователь не зарегистрирован, то возвращается пустая строка.
    """

    if _users.get(client_user) is None:
        return ""

    return _users[client_user]


def get_salt_from_hash(client_user: str) -> str:
    """
    Возвращает соль для пароля.
    Если пользователь не зарегистрирован, то возвращается пустая строка.
    """

    token_hash = get_password_hash(client_user)

    return token_hash[:64] if token_hash else ""


_users = get_settings("registered_users")
