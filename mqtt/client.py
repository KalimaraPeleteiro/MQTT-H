import time
import json

import paho.mqtt.client as mqtt

from random import randint


# Global Settings
BROKER = "localhost"
BROKER_PORT = 1883
TOPIC = "test/topic"
NUM_MESSAGES = 10000

connection_time = 0


# Client Functions
def on_connect(client, userdata, flags, rc):
    global connection_time
    connection_time = time.time() - userdata['connect_start_time']
    print("Conectado ao Broker Resultado de Código " + str(rc))

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
client.user_data_set({'connect_start_time': time.time()})
client.on_connect = on_connect
client.on_publish = on_publish


client.connect(BROKER, BROKER_PORT)
client.loop_start()
time.sleep(1)

publish_messages()

print(f"\n--- Métricas ---")
print(f"Tempo para Conexão: {connection_time:.4f} segundos")