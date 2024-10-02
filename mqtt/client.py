import time
import json

import paho.mqtt.client as mqtt

from random import randint


# Global Settings
BROKER = "localhost"
TOPIC = "test/topic"
NUM_MESSAGES = 10000

# Client Functions
def on_connect(client, userdata, flags, rc):
    print("Connectado ao Broker Resultado de Código " + str(rc))


def on_publish(client, userdata, mid):
    print(f"Mensagem Publicada com ID {mid}")

def publish_messages():
    for i in range(NUM_MESSAGES):
        data = {
            "a": randint(1, 1000),
            "b": randint(1, 1000),
            "timestamp": time.time()
        }
        client.publish(TOPIC, json.dumps(data))

        time.sleep(0.1)
    
    client.disconnect()


# Client
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

client.connect(BROKER)

publish_messages()