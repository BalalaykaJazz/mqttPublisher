FROM python:3.7-alpine3.8

RUN pip install paho-mqtt

# COPY ./requirements.txt /src/
COPY ./pod_mqtt_publisher /src/

RUN ["mkdir", "/src/logs"]
CMD ["python", "/src/mqtt_publisher_run.py"]