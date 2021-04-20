"""This module is used to post messages to mqtt broker"""
from socket import gaierror
import paho.mqtt.client as mqtt  # type: ignore
from event_logger import get_logger  # type: ignore

event_log = get_logger("__mqtt_writer__")


class MQTTConnectionError(Exception):
    """Common class for mqtt connection errors"""


class MqttConnection:
    """Context manager for connect to mqtt broker"""

    def __init__(self, settings):
        self.settings = settings
        self._client = mqtt.Client()

    def __enter__(self):
        try:
            self._client.tls_set(**self.settings.get("tls"))
            self._client.connect(**self.settings.get("broker_settings"))
        except gaierror as err:
            raise MQTTConnectionError from err
        except OSError as err:
            raise MQTTConnectionError from err
        except TypeError as err:
            raise MQTTConnectionError from err

        self._client.loop_start()
        return self._client

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.disconnect()


def publish_to_mqtt(report: tuple, settings: dict) -> bool:
    """
    Publish one message to mqtt broker. Return message sending result.

    report: tuple (topic: str, message: str)

    settings: dict (broker_settings: dict, tls: dict)
    broker_settings: dict (host: str, port: int, keepalive: int)
    tls: dict (ca_certs: str, certfile: str, keyfile: str)
    """

    try:
        with MqttConnection(settings) as client:
            topic, message = report
            info = client.publish(topic, message, qos=1)
            info.wait_for_publish()  # The message is guaranteed to be sent

            event_log.info("The message %s was published to %s", message, topic)

    except MQTTConnectionError as err:
        event_log.error("MQTT connection error. Can't publish message. Reason: %s", str(err))
        return False

    return info.is_published()
