"""Testando o tamanho de um contexto Tenseal em Bytes, para Envio via MQTT."""
import tenseal as ts

context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=4096)
context.global_scale = 2 ** 40

context_serialized = context.serialize(save_public_key=True, save_secret_key=False)

print(f"O tamanho em Bytes do contexto serializado é {len(context_serialized)}")