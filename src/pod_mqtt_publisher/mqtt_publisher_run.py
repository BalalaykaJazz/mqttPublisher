#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Mqtt publisher открывает и слушает сокет. Если приходит сообщение для устройства,
то оно публикуется в  mqtt брокер.
"""

from message_listener import start_listening

if __name__ == "__main__":
    start_listening()
