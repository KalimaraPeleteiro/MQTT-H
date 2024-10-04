import struct


def extract_connect_message_fields(message):
    """
    Lida com conexões. A estrutura de um CONNECT packet segue abaixo.
    
    1 Byte -> Header Fixo
    1 Byte -> Tamanho Restante
    6 Bytes -> Nome do Protocolo
    1 Byte -> Nível do Protocolo
    1 Byte -> Flags de Conexão
    2 Bytes -> Keep Alive?
    Variável de Identificação do Cliente.
    """

    if len(message) < 14:
        return None

    fields = {}

    try:
        # Header Fixo
        fields['remaining_length'] = message[1]

        # Tamanho do Protocolo
        protocol_name_length = struct.unpack("!B", message[9:10])[0]
        fields['protocol_name_length'] = protocol_name_length

        # O tamanho esperado mínimo para MQTT.
        if protocol_name_length != 4: 
            return None

        # Nome do Protocolo
        fields['protocol_name'] = message[10:10 + protocol_name_length].decode()
        
        # Level do Protocolo (1 Byte)
        fields['protocol_level'] = message[10 + protocol_name_length]
        
        # Connect Flags (1 Byte)
        fields['connect_flags'] = message[11 + protocol_name_length]

        # Keep Alive (2 Bytes)
        fields['keep_alive'] = struct.unpack("!H", message[12 + protocol_name_length:14 + protocol_name_length])[0]
        
        # Tamanho do Client ID (2 bytes)
        client_id_length = struct.unpack("!H", message[14 + protocol_name_length:16 + protocol_name_length])[0]
        fields["client_id_length"] = client_id_length

        if len(message) >= 16 + protocol_name_length + client_id_length:
            fields['client_id'] = message[16 + protocol_name_length:16 + protocol_name_length + client_id_length].decode()
        else:
            fields['client_id'] = None

    except (struct.error, IndexError):
        return None

    return fields