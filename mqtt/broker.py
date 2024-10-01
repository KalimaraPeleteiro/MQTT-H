import time
import json
import psutil
import statistics

import paho.mqtt.client as mqtt


# Global Settings
BROKER_PORT = 1883
TOPIC = "test/topic"
MAX_MESSAGES = 1000000


# Metrics
metrics = {
    'message_delivery_time': [],
    'rtt_list': [],
    'establish_time': [],
    'num_connections': 0,
}

message_count = 0


# Broker Functions
def on_connect(client, userdata, flags, rc):
    metrics['num_connections'] += 1
    print(f"Cliente Conectado: {client._client_id} | Resultado da Conexão: {rc}")

def on_disconnect(client, userdata, rc):
    metrics['num_connections'] -= 1
    print(f"Cliente Disconectado: {client._client_id}")

def on_publish(client, userdata, mid):
    publish_time = time.time()
    rtt = publish_time - client.start_time
    metrics['rtt_list'].append(rtt)
    print(f"Mensagem publicada com ID {mid} | RTT: {rtt:.4f} segundos")


def on_message(client, userdata, msg):
    global message_count

    payload = msg.payload.decode()

    try:
        data = json.loads(payload)
        timestamp = data['timestamp']
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Erro ao decodificar mensagem: {e}")
        return

    delivery_time = time.time() - timestamp
    metrics['message_delivery_time'].append(delivery_time)
    message_count += 1
    print(f"Menssagem recebida: {data['message']} | Tempo de entrega: {delivery_time:.4f} segundos")

    # Stop the broker after receiving the maximum number of messages
    if message_count >= MAX_MESSAGES:
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

while message_count < MAX_MESSAGES:
    time.sleep(0.1)

broker.loop_stop()

cpu_usage = psutil.cpu_percent()
memory_usage = psutil.virtual_memory().percent
average_rtt = statistics.mean(metrics['rtt_list']) if metrics['rtt_list'] else 0
average_delivery_time = statistics.mean(metrics['message_delivery_time']) if metrics['message_delivery_time'] else 0

print(f"\n--- Métricas ---")
print(f"Uso de CPU: {cpu_usage}%")
print(f"Uso de Memória: {memory_usage}%")
# print(f"Média de RTT: {average_rtt:.4f} seconds")
print(f"Média de Entrega de Mensagens: {average_delivery_time:.4f} seconds")
print(f"Média de Entrega de Mensagens 02: {sum(metrics['message_delivery_time'])/MAX_MESSAGES:.4f}")
# print(f"Conexões Ativas: {metrics['num_connections']}")
