FROM python

WORKDIR /app

COPY requirements.txt /app
COPY src /app/src

RUN pip install -r /app/requirements.txt
RUN ["mkdir", "/app/src/mqtt_pub/logs"]
CMD ["python", "/app/src/mqtt_publisher_run.py"]