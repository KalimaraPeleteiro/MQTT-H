"O listener é um agente que se inscreve no canal de confirmação e mede o RTT"
import time
import json
import statistics

import paho.mqtt.client as mqtt


# Constantes
MAX_MESSAGES = 1000000
BROKER = "localhost"
TOPIC = "test/topic"
ACK_TOPIC = "ack/topic"
METRICS = {
    'rtt_time': []
}
MESSAGE_COUNT = 0


# Client Functions
def on_connect(client, userdata, flags, rc):
    print("Connectado ao Broker Resultado de Código " + str(rc))


def on_message(client, userdata, msg):
    global MESSAGE_COUNT

    MESSAGE_COUNT += 1

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
        METRICS["rtt_time"].append(rtt)


listener = mqtt.Client()
listener.on_connect = on_connect
listener.on_message = on_message

listener.connect(BROKER)
listener.subscribe(ACK_TOPIC) 

listener.loop_start()


while MESSAGE_COUNT < MAX_MESSAGES:
    time.sleep(0.1)

listener.loop_stop()


average_rtt_time = statistics.mean(METRICS['rtt_time']) if METRICS['rtt_time'] else 0
print(f"\n--- Métricas ---")
print(f"Média de Round Trip Time (RTT): {average_rtt_time:.4f} segundos")