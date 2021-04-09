#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Begins listening on a socket. If a message arrives, it is published in the broker
"""

from message_listener import start_listening

if __name__ == "__main__":
    start_listening()

# TODO: unittest
