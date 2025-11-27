FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY arduino_mqtt_sub.py .

CMD [ "python", "arduino_mqtt_sub.py" ]
