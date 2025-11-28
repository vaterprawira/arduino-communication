import paho.mqtt.client as mqtt
import serial
import time
from datetime import datetime

# Serial Arduino
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600
ser = None

# MQTT Broker
#MQTT_BROKER = "10.1.33.26"
MQTT_BROKER = "10.1.11.225"
MQTT_PORT = 1883
MQTT_TOPIC_STATE = "mqtt/state"
MQTT_TOPIC_TIME = "mqtt/timestamp"

last_state = None
last_timestamp = None

def on_connect(client, userdata, flags, rc, properties=None):
    print(f"Connect: {rc}")
    client.subscribe([
        (MQTT_TOPIC_STATE, 0),
        (MQTT_TOPIC_TIME, 0)
    ])
    print("Subscribe:", MQTT_TOPIC_STATE, ",", MQTT_TOPIC_TIME)

def on_message(client, userdata, msg):
    global last_state, last_timestamp

    payload = msg.payload.decode()
    topic = msg.topic

    # STATE
    if topic == MQTT_TOPIC_STATE:
        last_state = payload
        print(f"\nSTATE = {last_state}")

    # TIMESTAMP
    elif topic == MQTT_TOPIC_TIME:
        last_timestamp = payload
        print(f"TIME  = {last_timestamp}")

        # Hitung delay
        try:
            t_send = datetime.strptime(last_timestamp, "%H:%M:%S.%f")
            t_now = datetime.now()
            diff_ms = (t_now - t_send).total_seconds() * 1000
            print(f"[DELAY] State={last_state} | Δ={diff_ms:.2f} ms")
        except:
            print("Timestamp format error.")

    # Kirim ke Arduino
    if ser and ser.is_open:
        ser.write(f"{payload}\n".encode())
    else:
        print("Serial not open.")

def main():
    global ser
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print("Serial connected:", SERIAL_PORT)
    except:
        print("Failed open serial")
        return

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        print("Broker error:", e)
        return

    client.loop_forever()

if __name__ == '__main__':
    main()
