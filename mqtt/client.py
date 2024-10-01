import time
import json

import paho.mqtt.client as mqtt



# Global Settings
BROKER = "localhost"
TOPIC = "test/topic"
NUM_MESSAGES = 10000


# Client Functions
def on_connect(client, userdata, flags, rc):
    print("Connectado ao Broker Resultado de Código " + str(rc))

def on_publish(client, userdata, mid):
    print(f"Mensagem Publicada com ID {mid}")


# Client
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

client.connect(BROKER)


# Publishing Messages
for i in range(NUM_MESSAGES):
    data = {
        "message": f"Mensagem {i + 1}",
        "timestamp": time.time()
    }
    client.publish(TOPIC, json.dumps(data))

    time.sleep(0.1)


client.disconnect()
