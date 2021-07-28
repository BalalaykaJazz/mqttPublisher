FROM python

WORKDIR /app

COPY mqtt_publisher_run.py /app
COPY requirements.txt /app
COPY src /app/src

RUN pip install -r /app/requirements.txt
RUN ["mkdir", "/app/src/mqtt_pub/logs"]
# RUN ["mkdir", "/app/src/mqtt_pub/settings"]
COPY src/mqtt_pub/settings/users.json /app/src/mqtt_pub/settings

CMD ["python", "mqtt_publisher_run.py"]