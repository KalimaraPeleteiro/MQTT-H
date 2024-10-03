"""O broker é o servidor na arquitetura MQTT."""
import time
import json
import psutil
import statistics

import paho.mqtt.client as mqtt


# Constantes
MAX_MESSAGES = 1000000
BROKER_PORT = 1883
TOPIC = "test/topic"
ACK_TOPIC = "ack/topic"
METRICS = {
    'message_delivery_time': [],
    'payload_size': []
}
MESSAGE_COUNT = 0


# Callbacks do Broker
def on_connect(client, userdata, flags, rc):
    print(f"Cliente Conectado: {client._client_id} | Resultado da Conexão: {rc}")


def on_disconnect(client, userdata, rc):
    print(f"Cliente Disconectado: {client._client_id}")


def on_publish(client, userdata, mid):
    print(f"Mensagem publicada com ID {mid}")


def on_message(client, userdata, msg):
    global MESSAGE_COUNT

    payload = msg.payload.decode()

    try:
        data = json.loads(payload)
        sum_result = data['a'] + data['b']
        print(f"O resultado de {data['a']} + {data['b']} é {sum_result}")
        timestamp = data['timestamp']
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Erro ao decodificar mensagem: {e}")
        return

    delivery_time = time.time() - timestamp
    METRICS['message_delivery_time'].append(delivery_time)

    # Coletando o tamanho do Payload em Bytes.
    payload_in_bytes = len(payload.encode('utf-8'))
    METRICS['payload_size'].append(payload_in_bytes)

    MESSAGE_COUNT += 1
    print(f"Menssagem recebida | Tempo de entrega: {delivery_time:.4f} segundos")

    # Retorno de Sucesso para calcular RTT
    acknowledgment_data = {
        "status": "acknowledged",
        "timestamp": timestamp          
    }
    client.publish(ACK_TOPIC, json.dumps(acknowledgment_data))

    # Broker é interrompido após número máximo de mensagens.
    if MESSAGE_COUNT >= MAX_MESSAGES:
        client.disconnect()


broker = mqtt.Client()

broker.on_connect = on_connect
broker.on_disconnect = on_disconnect
broker.on_publish = on_publish
broker.on_message = on_message

broker.start_time = time.time()
broker.connect('localhost', BROKER_PORT)
broker.subscribe(TOPIC)
broker.loop_start()

print("Broker está rodando, aguardando mensagens...")

while MESSAGE_COUNT < MAX_MESSAGES:
    time.sleep(0.1)

broker.loop_stop()

cpu_usage = psutil.cpu_percent()
memory_usage = psutil.virtual_memory().percent
average_delivery_time = statistics.mean(METRICS['message_delivery_time']) if METRICS['message_delivery_time'] else 0
average_payload_size = statistics.mean(METRICS['payload_size']) if METRICS['payload_size'] else 0

print(f"\n--- Métricas ---")
print(f"Uso de CPU: {cpu_usage}%")
print(f"Uso de Memória: {memory_usage}%")
print(f"Média de Entrega de Mensagens: {average_delivery_time:.4f} segundos")
print(f"Média de Tamanho das Mensagens: {average_payload_size:4f} Bytes")
