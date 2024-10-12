"""O cliente é um agente que se conecta ao broker para enviar mensagens pelo canal."""
import time
import uuid
import sys
import logging 
import json 

import tenseal as ts
import paho.mqtt.client as mqtt


# Constantes
BROKER = "localhost"
BROKER_PORT = 1883
CONNECTION_TIME = 0     # Métrica de Tempo para Conexão
CLIENT_ID = uuid.uuid4()
RECEIVED_CONTEXT_BATCHES = []

logging.basicConfig(level=logging.DEBUG)


# Client Callbacks
def on_connect(client, userdata, flags, rc):
    global CONNECTION_TIME
    CONNECTION_TIME = time.time() - userdata['connect_start_time']
    print("Conectado ao Broker Resultado de Código " + str(rc))


def on_publish(client, userdata, mid):
    print(f"Mensagem Publicada com ID {mid}")


def on_message(client, userdata, msg):
    if msg.topic == "he/public-key":
        batch_payload = msg.payload
        RECEIVED_CONTEXT_BATCHES.append(batch_payload)
        print(f"Batch recebido: {len(batch_payload)} Bytes.")

        if len(batch_payload) < 4096:
            complete_context = b''.join(RECEIVED_CONTEXT_BATCHES)
            he_context = ts.Context.load(complete_context)
            print(f"Contexto Completo Recebido e Re-estruturado.")


client = mqtt.Client(client_id=f"client-{CLIENT_ID}")
client.user_data_set({'connect_start_time': time.time()})
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message
client.enable_logger()


if client.connect(BROKER, BROKER_PORT) != 0:
    print("Falha ao Conectar ao Broker!")
    sys.exit(0)
else:
    client.loop_start()
    client.subscribe(f"he/public-key/{CLIENT_ID}")
    time.sleep(1)
    client.subscribe("teste")
    time.sleep(1)
    client.publish("he/retrieve-key", str(CLIENT_ID))
    time.sleep(2)
    client.unsubscribe(f"he/public-key/{CLIENT_ID}")
    time.sleep(2)
    json_payload = {
        "Mensagem": "Esse é um teste",
        "ID": str(CLIENT_ID)
    }
    json_string = json.dumps(json_payload)  # Convert dict to JSON string
    client.publish("teste", payload=json_string)  # Publish JSON string
    time.sleep(2)


print(f"\n--- Métricas ---")
print(f"Tempo para Conexão: {CONNECTION_TIME:.4f} segundos")