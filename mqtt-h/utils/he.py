"""Funções Homomórficas de Criptografia"""

import tenseal as ts


def generate_keys():
    """
    Gerando Par de Chaves para esquema CKKS (Cheon-Kim-Kim-Song)

    poly_modulus_degree: Valores maiores permitem a encriptação simultânea de mais valores, à custo
    de mais memória e demanda computacional.

    plain_modulus: Influencia a segurança e o limite de número que é possível encriptar.

    global_scale: Escala de precisão.
    """
    
    context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=4096, plain_modulus=256)
    context.global_scale = 2 ** 40

    public_key, private_key = context.public_key(), context.secret_key()
    return public_key, private_key