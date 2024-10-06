"""Funções Homomórficas de Criptografia"""

import tenseal as ts


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