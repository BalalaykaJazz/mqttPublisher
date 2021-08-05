"""Модуль используется для загрузки настроек, необходимых для корректной работы сервиса."""
import os
import json
from pydantic import BaseSettings

REGISTERED_USERS_PATH = "settings/users.json"
TLS_CA_CERTS_PATH = "settings/tls_ca_certs.crt"
TLS_CERTFILE_PATH = "settings/tls_certfile.crt"
TLS_KEYFILE_PATH = "settings/tls_keyfile.key"
SSL_KEYFILE_PATH = "settings/server_key.pem"
SSL_CERTFILE_PATH = "settings/server_cert.pem"


def get_full_path(file_name: str) -> str:
    """Return full path to file"""
    return os.path.join(os.path.dirname(__file__), file_name)


def get_registered_users(registered_users_path: str) -> dict:
    """
    Возвращает словарь зарегистрированных пользователей для подключения к сокету.
    Ключ - имя пользователя; Пароль - хэш пароля."""

    with open(get_full_path(registered_users_path), encoding="utf-8") as file:
        requested_settings = json.load(file)

    return requested_settings


def get_settings_to_socket() -> dict:
    """Получение настроек для работы сокета"""

    return {"socket_host": settings.socket_host,
            "socket_port": settings.socket_port,
            "use_ssl": settings.use_ssl,
            "ssl_keyfile_path": settings.ssl_keyfile_path,
            "ssl_certfile_path": settings.ssl_certfile_path}


def get_settings_to_publish() -> dict:
    """Получение настроек для работы брокера"""

    broker_settings = {"host": settings.broker_host,
                       "port": settings.broker_port,
                       "keepalive": settings.broker_keep_alive}

    tls = {"ca_certs": settings.tls_ca_certs_path,
           "certfile": settings.tls_certfile_path,
           "keyfile": settings.tls_keyfile_path}

    return {"broker_settings": broker_settings,
            "broker_use_tls": settings.broker_use_tls,
            "tls": tls}


class Settings(BaseSettings):  # pylint: disable = too-few-public-methods
    """
    Параметры подключения к внешним ресурсам.

    mqtt_settings - подключение к брокеру mqtt для получения сообщений от устройств.
    broker_host - адрес mqtt брокера.
    broker_port - порт mqtt брокера.
    broker_use_tls - Признак использования tls для соединения с брокером.
    broker_keep_alive - Период активности соединения.

    socket_settings - сокет, который слушает mqtt_publisher.
    socket_host - ip адрес сокета, к которому подключается клиент.
    socket_port - порт сокета, к которому подключается клиент.
    use_ssl - Признак использования ssl для соединения с сокетом.
    """

    # mqtt_settings
    broker_host: str = ""
    broker_port: int = 8883
    broker_use_tls: bool = False
    broker_keep_alive: int = 60
    tls_ca_certs_path: str = get_full_path(TLS_CA_CERTS_PATH)
    tls_certfile_path: str = get_full_path(TLS_CERTFILE_PATH)
    tls_keyfile_path: str = get_full_path(TLS_KEYFILE_PATH)

    # socket_settings
    socket_host: str = "127.0.0.1"
    socket_port: int = 5000
    use_ssl: bool = False
    ssl_keyfile_path: str = get_full_path(SSL_KEYFILE_PATH)
    ssl_certfile_path: str = get_full_path(SSL_CERTFILE_PATH)


settings = Settings(_env_file=get_full_path(".env"),
                    _env_file_encoding="utf-8")

registered_users = get_registered_users(REGISTERED_USERS_PATH)
