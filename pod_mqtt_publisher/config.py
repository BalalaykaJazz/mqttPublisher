"""This module is used to prepare settings"""
import os
import json

MQTT_SETTINGS_PATH = "settings/mqtt_settings.json"
SOCKET_SETTINGS_PATH = "settings/socket_settings.json"
TLS_CA_CERTS_PATH = "settings/ca.crt"
TLS_CERTFILE_PATH = "settings/donoff.crt"
TLS_KEYFILE_PATH = "settings/donoff.key"
SSL_KEYFILE_PATH = "settings/ssl.key"
SSL_CERTFILE_PATH = "settings/ssl.crt"


def get_full_path(file_name: str) -> str:
    """Return full path to file"""
    return os.path.join(os.path.dirname(__file__), file_name)


def get_settings(setting_name: str) -> dict:
    """Return settings for connecting to mqtt broker"""

    if setting_name == "settings_to_publish":
        with open(get_full_path(MQTT_SETTINGS_PATH), encoding="utf-8") as file:
            settings = json.load(file)

        if settings.get("use_tls"):
            tls = {"ca_certs": get_full_path(TLS_CA_CERTS_PATH),
                   "certfile": get_full_path(TLS_CERTFILE_PATH),
                   "keyfile": get_full_path(TLS_KEYFILE_PATH)}
        else:
            tls = {}

        requested_settings = {"broker_settings": settings.get("broker_settings"), "tls": tls}

    elif setting_name == "settings_to_socket":
        with open(get_full_path(SOCKET_SETTINGS_PATH), encoding="utf-8") as file:
            settings = json.load(file)

        requested_settings = {"host": settings.get("host"),
                              "port": settings.get("port"),
                              "use_ssl": settings.get("use_ssl")}

        if requested_settings.get("use_ssl"):
            requested_settings["ssl.key"] = get_full_path(SSL_KEYFILE_PATH)
            requested_settings["ssl.crt"] = get_full_path(SSL_CERTFILE_PATH)

    else:
        requested_settings = {}

    return requested_settings
