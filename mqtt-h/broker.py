"""O Broker age como o servidor na arquitetura do MQTT."""
import socket
import struct
import signal
import sys

from utils.he import generate_context
from utils.connection_package import extract_connect_message_fields
from utils.publish_package import extract_publish_message_fields


# Constantes
CLIENTS = dict()
SERVER_SOCKET = None
BATCH_SIZE = 4096


def signal_handler(sig, frame):
    """Encerra o Broker em um CTRL + C."""
    global SERVER_SOCKET

    print("\nEncerrando o Broker...")

    if SERVER_SOCKET:
        SERVER_SOCKET.close()
    sys.exit(0)


def start_broker(host='0.0.0.0', port=1883):
    """
    Inicia o Broker.
    
    host: Endereço de Início
    port: Porta em que será iniciado.
    """

    global SERVER_SOCKET
    SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER_SOCKET.bind((host, port))
    SERVER_SOCKET.listen()
    SERVER_SOCKET.settimeout(1.0)

    print(f"Broker inicializado em {host}:{port}.")

    # Loop Infinito de escuta (Esperando por Mensagens).
    while True:
        try:
            client_socket, address = SERVER_SOCKET.accept()
            print(f"Conexão vinda de {address}.")
            handle_client(client_socket)
        except socket.timeout:
            continue
        

def handle_client(client_socket):
    """
    Lida com mensagens que chegam ao broker.

    client_socket: O socket do cliente que enviou a mensagem.
    """

    while True:
        message = client_socket.recv(1024)
        if not message:
            break
    
        # Em MQTT, o primeiro byte define o tipo do pacote.
        packet_type = message[0] >> 4
        if packet_type == 1:
            handle_connect(client_socket, message)
        elif packet_type == 3:
            handle_publish(client_socket, message)


def handle_connect(client_socket, message):
    """
    Lida com requisições de conexão. Extrai os campos da mensagem, e se ela for válida, gera um par de chaves criptográficas e dedica aquele cliente.
    Caso a mensagem seja válida, devolve um resultado de Conexão Aceita (CONNACK) para o cliente.

    client_socket: O socket do cliente que enviou a mensagem.
    message: Mensagem enviada.
    """

    print("\nConexão Requisitada!")

    fields = extract_connect_message_fields(message)
    if fields is None:
        print(f"Erro ao extrair campos da mensagem de conexão. Mensagem: {message.hex()}")
        return

    print(f"Mensagem de Conexão com protocolo {fields['protocol_name']}, e ID de cliente {fields['client_id']}.")

    print("Gerando Par de Chaves Criptográficas...")
    context = generate_context()
    CLIENTS[client_socket] = {"client_id": fields["client_id"], "he_context": context}

    # Resposta de Connect Acception (CONNACK)
    connack_response = struct.pack("!BB", 32, 2) + struct.pack("!BB", 0, 0)
    client_socket.send(connack_response)
    print("Enviando CONNACK...\n")


def encode_remaining_length(length):
    encoded = bytearray()
    while True:
        byte = length % 128
        length = length // 128
        if length > 0:
            byte |= 128
        encoded.append(byte)
        if length == 0:
            break
    return encoded


def handle_publish(client_socket, message):
    """
    Lida com requisições de publicação. Extrai os campos da mensagem, e se ela for válida, gerencia a depender do tópico da mensagem.

    client_socket: O socket do cliente que enviou a mensagem.
    message: Mensagem enviada.
    """

    print("\nMensagem Recebida!")

    fields = extract_publish_message_fields(message)
    if fields is None:
        print(f"Erro ao extrair campos da mensagem: {message.hex()}")
        return

    print(f"Mensagem recebida no tópico '{fields['topic']}'.")

    if fields['topic'] == "he/retrieve-key":
        if client_socket in CLIENTS.keys():
            context = CLIENTS[client_socket]['he_context']
            response_topic = "he/public-key"
            serialized_context = context.serialize(save_public_key = True, save_secret_key = False)

            total_size = len(serialized_context)
            num_batches = (total_size + BATCH_SIZE - 1) // BATCH_SIZE

            for i in range(num_batches):
                start_index = i * BATCH_SIZE
                end_index = min(start_index + BATCH_SIZE, total_size)
                batch_payload = serialized_context[start_index:end_index]

                # Construct MQTT PUBLISH packet
                packet_type = 0x30  # PUBLISH
                topic_len = len(response_topic)
                remaining_length = 2 + topic_len + len(batch_payload)  # 2 bytes for topic length

                # Fixed header
                response_message = struct.pack("!B", packet_type)
                response_message += encode_remaining_length(remaining_length)

                # Variable header
                response_message += struct.pack("!H", topic_len)
                response_message += response_topic.encode()

                # Payload
                response_message += batch_payload

                client_socket.send(response_message)
                print(f"Enviando o batch {i + 1}/{num_batches}, com o tamanho de {len(batch_payload)} B")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    start_broker()