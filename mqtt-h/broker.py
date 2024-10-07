"""
Essa é uma classe que emula o funcionamento de um Broker dentro do contexto do Protocolo MQTT. O protocolo
MQTT é um protocolo de inscrição e publicação para comunicação de baixo custo entre dispositivos embarcados.
Essa implementação adiciona a esse protocolo o uso de Criptografia Homomórfica, para aumento de privacidade
dos dados e a segurança das comunicações.
"""
import socket
import struct
import signal
import sys

import tenseal as ts


class MQTTHBroker:

    def __init__(self, host="0.0.0.0", port=1883, strict_mode=True) -> None:
        self.host = host
        self.port = port
        self.clients = {}
        self.server_socket = None
        self.strict_mode = strict_mode


    def start(self):
        """Função que inicializa o broker."""
        self.setup_signal_handler()
        self.initialize_server()
        self.listen_for_clients()


    def setup_signal_handler(self):
        """Aguarda pelo comando de CTRL + C para encerrar o Broker da maneira correta."""
        signal.signal(signal.SIGINT, self.shutdown_broker)
    

    def shutdown_broker(self, sig, frame):
        """Encerra o broker."""
        print("\nEncerrando o Broker...")
        
        if self.server_socket:
            self.server_socket.close()
        sys.exit(0)
    

    def initialize_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        self.server_socket.settimeout(1.0)
        print(f"Broker iniciado em {self.host}, na porta {self.port}.")
    

    def listen_for_clients(self):
        """Aguarda por mensagens de clientes."""
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                print(f"Conexão vinda de {address} detectada.")
                self.handle_client(client_socket)
            except socket.timeout:
                continue
    

    def handle_client(self, client_socket):
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
                self.handle_connect(client_socket, message)
            elif packet_type == 3:
                self.handle_publish(client_socket, message)
        
    
    def handle_connect(self, client_socket, message):
        """
        Lida com requisições de conexão. Extrai os campos da mensagem, e se ela for válida, gera um par de chaves criptográficas e dedica aquele cliente.
        Caso a mensagem seja válida, devolve um resultado de Conexão Aceita (CONNACK) para o cliente.

        client_socket: O socket do cliente que enviou a mensagem.
        message: Mensagem enviada.
        """
        print("\nConexão Requisitada!")

        fields = self.extract_connect_message_fields(message)
        if fields is None:
            print(f"Erro ao extrair campos da mensagem de conexão. Mensagem: {message.hex()}")
            return

        print(f"Mensagem de Conexão com protocolo {fields['protocol_name']}, e ID de cliente {fields['client_id']}.")

        print("Gerando Par de Chaves Criptográficas...")
        context = self.generate_context()
        self.clients[client_socket] = {"client_id": fields["client_id"], "he_context": context}

        # Resposta de Connect Acception (CONNACK)
        connack_response = struct.pack("!BB", 32, 2) + struct.pack("!BB", 0, 0)
        client_socket.send(connack_response)
        print("Enviando CONNACK...\n")
    

    @staticmethod
    def extract_connect_message_fields(message):
        """
        Lida com conexões. A estrutura de um CONNECT packet segue abaixo.
        
        1 Byte -> Header Fixo
        1 Byte -> Tamanho Restante
        2 Bytes -> Tamanho do Nome do Protocolo (N)
        N Bytes -> Nome do Protocolo
        1 Byte -> Nível do Protocolo
        1 Byte -> Flags de Conexão
        2 Bytes -> Keep Alive?

        Variável de Identificação do Cliente (Pode existir ou não).
        2 Bytes -> Tamanho do Client ID (M)
        M Bytes -> Client ID [Nesse caso, será um UUID04]
        """
        fields = {}

        try:
            # Header Fixo
            fields['fixed_header'] = message[0]

            # Tamanho Restante
            fields['remaining_length'] = message[1]

            # Tamanho do Nome do Protocolo
            protocol_name_length = struct.unpack("!H", message[2:4])[0]
            fields['protocol_name_length'] = protocol_name_length

            # Nome do Protocolo
            fields['protocol_name'] = message[4:4 + protocol_name_length].decode('utf-8')
            
            # Level do Protocolo (1 Byte)
            fields['protocol_level'] = message[4 + protocol_name_length]
            
            # Connect Flags (1 Byte)
            fields['connect_flags'] = message[5 + protocol_name_length]

            # Keep Alive (2 Bytes)
            fields['keep_alive'] = struct.unpack("!H", message[6 + protocol_name_length:8 + protocol_name_length])[0]
            
            # Tamanho do Client ID (2 bytes)
            client_id_length = struct.unpack("!H", message[8 + protocol_name_length:10 + protocol_name_length])[0]
            fields["client_id_length"] = client_id_length

            fields['client_id'] = message[10 + protocol_name_length:10 + protocol_name_length + client_id_length].decode('utf-8')

        except (struct.error, IndexError) as e:
            print(f"Erro ao processar a mensagem: {e}")
            return None

        return fields


    @staticmethod
    def generate_context():
        """
        Gerando Contexto para esquema CKKS (Cheon-Kim-Kim-Song)

        poly_modulus_degree: Valores maiores permitem a encriptação simultânea de mais valores, à custo
        de mais memória e demanda computacional.

        global_scale: Escala de precisão.


        - Porquê gerar o contexto e não as chaves? (Pública e Privada)
        Porquê é possível serializar e enviar o contexto pela rede como um bytearray, enquanto as chaves
        não provém essa interface. A partir do contexto, então, é possível retirar as chaves.
        """
        context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=4096)
        context.global_scale = 2 ** 40

        return context
    

    def handle_publish(self, client_socket, message):
        """
        Lida com requisições de publicação. Extrai os campos da mensagem, e se ela for válida, gerencia a depender do tópico da mensagem.

        client_socket: O socket do cliente que enviou a mensagem.
        message: Mensagem enviada.
        """

        print("\nMensagem Recebida!")

        fields = self.extract_publish_message_fields(message)
        if fields is None:
            print(f"Erro ao extrair campos da mensagem: {message.hex()}")
            return

        print(f"Mensagem recebida no tópico '{fields['topic']}'.")

        if fields['topic'] == "he/retrieve-key":
            self.send_he_context(client_socket)
    

    @staticmethod
    def extract_publish_message_fields(message):
        """
        Lida com Pacotes de Publicação. Em MQTT, eles possuem o seguinte formato:

        . Tamanho do Nome do Tópico
        . Nome do Tópico
        . Payload (Conteúdo)
        """
        fields = {}

        try:
            topic_length = struct.unpack("!H", message[2:4])[0]  
            fields["topic_length"] = topic_length
            fields["topic"] = message[4:4 + topic_length].decode('utf-8')  
            fields["payload"] = message[4 + topic_length:] 
        
        except (struct.error, IndexError) as e:
            print(f"Ao erro extrair campos da mensagem: {e}.")
            return None

        return fields

    
    def send_he_context(self, client_socket, BATCH_SIZE=4096):
        """
        Resposta à requisições feitas ao canal de retorno de chave. Envia o contexto 
        homomórfico público, caso o cliente tenha sido registrado. O envio é realizado em 
        batches, pois o contexto ultrapassa os 400KB, na maioria dos casos.
        """
        if client_socket in self.clients.keys():
            context = self.clients[client_socket]['he_context']
            response_topic = "he/public-key"
            serialized_context = context.serialize(save_public_key = True, save_secret_key = False)

            total_size = len(serialized_context)
            num_batches = (total_size + BATCH_SIZE - 1) // BATCH_SIZE

            for i in range(num_batches):
                start_index = i * BATCH_SIZE
                end_index = min(start_index + BATCH_SIZE, total_size)
                batch_payload = serialized_context[start_index:end_index]

                self.send_batch(client_socket, response_topic, batch_payload)
                print(f"Enviando o batch {i + 1}/{num_batches}, com o tamanho de {len(batch_payload)} B")



    def send_batch(self, client_socket, response_topic, batch_payload):
        """
        Função para o envio de batches.
        """
        packet_type = 0x30  # PUBLISH
        topic_len = len(response_topic)
        remaining_length = 2 + topic_len + len(batch_payload)  # 2 bytes for topic length

        # Fixed header
        response_message = struct.pack("!B", packet_type)
        response_message += self.encode_remaining_length(remaining_length)

        # Variable header
        response_message += struct.pack("!H", topic_len)
        response_message += response_topic.encode()

        # Payload
        response_message += batch_payload

        client_socket.send(response_message)
    

    @staticmethod
    def encode_remaining_length(length):
        """
        Função utilizada para codificar o tamanho restante de uma mensagem uma representação por bytes.
        Caso o tamanho restante seja de até 128, é possível representar isso em um único Byte. Caso contrário,
        é necessário separá-lo em múltiplos bytes.
        """
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



if __name__ == "__main__":
    broker = MQTTHBroker()
    broker.start()