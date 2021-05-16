"""This module is used to post messages to mqtt broker"""
from socket import gaierror
import multiprocessing  # type: ignore
from multiprocessing.queues import Queue as mQueue  # type: ignore
from datetime import datetime
import paho.mqtt.client as mqtt  # type: ignore
import paho.mqtt.subscribe as subscribe  # type: ignore
from event_logger import get_logger  # type: ignore

event_log = get_logger("__mqtt_writer__")
TIMEOUT_WAIT_MQTT = 15


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


def read_from_mqtt(settings: dict, topic: str) -> str:
    """
    Получим ответ из mqtt с помощью функции get_answer_from_mqtt.
    Функция является блокирующей, поэтому предусмотрим возможность отказаться от ожидания ответа.
    Для этого создаем процесс, и контролируем время его работы. Если оно превышает TIME_LIMIT, то
    останавливаем процесс.

    Возвращаемое значение: строка с полученным ответом или сообщением о таймауте.
    """

    ctx = multiprocessing.get_context('spawn')
    result_queue = ctx.Queue()
    proc = ctx.Process(target=get_answer_from_mqtt,
                       args=(result_queue,
                             topic,
                             settings.get("broker_settings"),
                             settings.get("tls")))
    proc.start()

    start = datetime.now()
    while (datetime.now() - start).seconds < TIMEOUT_WAIT_MQTT:
        if not proc.is_alive():
            answer = result_queue.get()
            break

    else:
        answer = "Таймаут получения ответа от брокера"
        proc.terminate()

    return answer


def get_answer_from_mqtt(reply_queue: mQueue,
                         topic: str,
                         broker_settings: dict,
                         tls: dict) -> None:
    """
    Функция subscribe.simple() получает ответ из mqtt, который помещается в очередь.
    """

    answer = subscribe.simple(topic,
                              hostname=broker_settings["host"],
                              port=broker_settings["port"],
                              retained=False,
                              msg_count=1,
                              tls=tls)

    event_log.info("Received message from topic %s", topic)
    reply_queue.put(answer.payload.decode())
