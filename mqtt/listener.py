import time
import json
import statistics

import paho.mqtt.client as mqtt


# Global Settings
BROKER = "localhost"
TOPIC = "test/topic"
ACK_TOPIC = "ack/topic"
MAX_MESSAGES = 1000000


metrics = {
    'rtt_time': []
}

message_count = 0

# Client Functions
def on_connect(client, userdata, flags, rc):
    print("Connectado ao Broker Resultado de Código " + str(rc))

def on_message(client, userdata, msg):
    global message_count

    message_count += 1

    if msg.topic == ACK_TOPIC:
        payload = msg.payload.decode()
        try:
            data = json.loads(payload)
            timestamp = data['timestamp']
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Erro ao decodificar mensagem: {e}")
            return
        print(f"Timestamp Recebido {timestamp}")
        rtt = time.time() - timestamp
        metrics["rtt_time"].append(rtt)


# Client
listener = mqtt.Client()
listener.on_connect = on_connect
listener.on_message = on_message

listener.connect(BROKER)
listener.subscribe(ACK_TOPIC) 

listener.loop_start()


while message_count < MAX_MESSAGES:
    time.sleep(0.1)

listener.loop_stop()


average_rtt_time = statistics.mean(metrics['rtt_time']) if metrics['rtt_time'] else 0
print(f"\n--- Métricas ---")
print(f"Média de Round Trip Time (RTT): {average_rtt_time:.4f} segundos")