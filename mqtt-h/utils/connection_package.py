"""Lidando com Conexões com Clientes."""

import struct


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