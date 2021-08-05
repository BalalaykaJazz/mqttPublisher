"""Тестирование файла config.py и ипользуемых в нем файлов настроек"""
import os
import pytest  # type: ignore
from src.mqtt_pub.config import settings as config, get_full_path  # type: ignore


@pytest.mark.parametrize("test_path", [config.tls_ca_certs_path,
                                       config.tls_certfile_path,
                                       config.tls_keyfile_path])
def test_config_tls(test_path):
    """Проверяем наличие файлов для TLS"""

    test_path = get_full_path(test_path)
    assert os.path.exists(test_path)
