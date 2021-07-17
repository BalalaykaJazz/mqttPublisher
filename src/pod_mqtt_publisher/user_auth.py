"""
Процедуры для авторизации в mqtt_publisher
"""

import hmac
from src.pod_mqtt_publisher.config import registered_users


def client_authenticate(client_user: str, received_token_hash: str) -> bool:
    """
    Аутентификация пользователя.
    Пользователь должен быть предварительно зарегистрирован в системе.
    Полученный от клиента хэш пароля должен совпадать с хешом на сервере.
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

    if registered_users.get(client_user) is None:
        return ""

    return registered_users[client_user]


def get_salt_from_hash(client_user: str) -> str:
    """
    Возвращает соль для пароля.
    Если пользователь не зарегистрирован, то возвращается пустая строка.
    """

    token_hash = get_password_hash(client_user)

    return token_hash[:64] if token_hash else ""
