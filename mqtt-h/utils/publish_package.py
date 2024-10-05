"""Lidando com Envios de Mensagens por Publicação"""

import struct 


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