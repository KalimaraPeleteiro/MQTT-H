import socket
import struct
import signal
import sys

from utils.he import generate_keys
from utils.connection_package import extract_connect_message_fields
from utils.publish_package import extract_publish_message_fields


# Constantes
CLIENTS = dict()
SERVER_SOCKET = None


def signal_handler(sig, frame):
    """Encerra o Broker em um CTRL + C."""
    global SERVER_SOCKET

    print("\nEncerrando o Broker...")

    if CLIENTS != {}:
        print(f"Lista de Clientes")
        print(CLIENTS)

    if SERVER_SOCKET:
        SERVER_SOCKET.close()
    sys.exit(0)


def start_broker(host='0.0.0.0', port=1883):
    global SERVER_SOCKET
    SERVER_SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    SERVER_SOCKET.bind((host, port))
    SERVER_SOCKET.listen()
    SERVER_SOCKET.settimeout(1.0)

    print(f"Broker inicializado em {host}:{port}.")

    # Loop Infinito de escuta.
    while True:
        try:
            client_socket, address = SERVER_SOCKET.accept()
            print(f"Conexão vinda de {address}.")
            handle_client(client_socket)
        except socket.timeout:
            continue
        

def handle_client(client_socket):
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
    print("\nConexão Detectada!")
    # print(f"Mensagem: {message.hex()}")

    fields = extract_connect_message_fields(message)
    if fields is None:
        print(f"Erro ao extrair campos da mensagem de conexão. Mensagem: {message.hex()}")
        return

    # print(f"Mensagem de Conexão com protocolo {fields['protocol_name']}, e ID de cliente {fields['client_id']}.")

    print("Gerando Par de Chaves Criptográficas...")
    pubKey, privKey = generate_keys()
    CLIENTS[client_socket] = {"client_id": fields["client_id"], "public_key": pubKey, "private_key": privKey}

    # Resposta de Connect Acception (CONNACK)
    connack_response = struct.pack("!BB", 32, 2) + struct.pack("!BB", 0, 0)
    client_socket.send(connack_response)
    print("Enviando CONNACK...\n")


def handle_publish(client_socket, message):
    print("\nMensagem Recebida!")

    fields = extract_publish_message_fields(message)
    if fields is None:
        print(f"Erro ao extrair campos da mensagem: {message.hex()}")
        return

    # print(f"Mensagem recebida no tópico '{fields['topic']}': {fields['payload'].decode('utf-8')}")

    if fields['topic'] == "he/retrieve-keys":
        if client_socket in CLIENTS.keys():
            print(f"Recebendo mensagem de cliente de chave pública {CLIENTS[client_socket]['public_key']}")


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    start_broker()