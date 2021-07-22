#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Mqtt publisher открывает и слушает сокет. Если приходит сообщение для устройства,
то оно публикуется в  mqtt брокер.
"""

from src.pod_mqtt_publisher import start_listening  # pylint: disable = import-error

if __name__ == "__main__":
    start_listening()
