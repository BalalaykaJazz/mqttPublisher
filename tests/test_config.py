"""Тестирование файла config.py и ипользуемых в нем файлов настроек"""
import os
import pytest  # type: ignore
from pod_mqtt_publisher import config  # type: ignore


@pytest.mark.parametrize("test_path", ["pod_mqtt_publisher/logs",
                                       "pod_mqtt_publisher/settings"])
def test_directory(test_path):
    """Проверяем наличие обязательных директорий"""

    assert os.path.isdir(test_path)


@pytest.mark.parametrize("test_path", [config.TLS_CA_CERTS_PATH,
                                       config.TLS_CERTFILE_PATH,
                                       config.TLS_KEYFILE_PATH])
def test_config_tls(test_path):
    """Проверяем наличие файлов для TLS"""

    test_path = config.get_full_path(test_path)
    assert os.path.exists(test_path)


@pytest.mark.parametrize("test_path", [config.MQTT_SETTINGS_PATH,
                                       config.SOCKET_SETTINGS_PATH])
def test_config_files(test_path):
    """Проверяем наличие конфигурационных файлов"""

    test_path = config.get_full_path(test_path)
    assert os.path.exists(test_path)


@pytest.mark.parametrize("name", ["settings_to_publish",
                                  "settings_to_socket",
                                  ""])
def test_get_settings(name):
    """Проверяем, что файлы настроек корректно считываются"""

    returned_value = config.get_settings(name)
    assert isinstance(returned_value, dict)
