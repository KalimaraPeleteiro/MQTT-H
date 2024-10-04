"""O cliente é um agente que se conecta ao broker para enviar mensagens pelo canal."""
import time
import json
import uuid
import sys

import paho.mqtt.client as mqtt

from random import randint


# Constantes
NUM_MESSAGES = 10
BROKER = "localhost"
TOPIC = "test/topic"
BROKER_PORT = 1883
CONNECTION_TIME = 0     # Métrica de Tempo para Conexão


# Client Functions
def on_connect(client, userdata, flags, rc):
    global CONNECTION_TIME
    CONNECTION_TIME = time.time() - userdata['connect_start_time']
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


client_id = uuid.uuid4()
client = mqtt.Client(client_id=f"client-{client_id}")
client.user_data_set({'connect_start_time': time.time()})
client.on_connect = on_connect
client.on_publish = on_publish

if client.connect(BROKER, BROKER_PORT) != 0:
    print("Falha ao Conectar ao Broker!")
    sys.exit(0)
else:
    client.loop_start()
    time.sleep(1)

    publish_messages()


print(f"\n--- Métricas ---")
print(f"Tempo para Conexão: {CONNECTION_TIME:.4f} segundos")