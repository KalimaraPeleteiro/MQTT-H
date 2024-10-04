import socket
import struct
import signal
import sys

from utils.connection_package import extract_connect_message_fields


# Constantes
CLIENTS = dict()
SERVER_SOCKET = None


def signal_handler(sig, frame):
    global SERVER_SOCKET

    print("\nEncerrando o Broker...")
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
            pass


def handle_connect(client_socket, message):
    print("Conexão Detectada!")
    print(f"Mensagem: {message.hex()}")

    fields = extract_connect_message_fields(message)
    if fields is None:
        print("Erro ao extrair campos da mensagem de conexão.")
        return

    print(f"Fields\n{fields}")    
    protocol_name = fields['protocol_name']
    client_id = fields['client_id']

    print(f"Mensagem de Conexão com protocolo {protocol_name}, e ID de cliente {client_id}.")

    # Resposta de Connect Acception
    connack_response = struct.pack("!BB", 32, 0)
    client_socket.send(connack_response)
    print(f"Enviando {connack_response}")

    CLIENTS[client_socket] = []


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    start_broker()