"""Validação de Contexto usando apenas Chave Pública"""
import tenseal as ts

def create_context():
    context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=4096, plain_modulus=256)
    context.global_scale = 2 ** 40  
    return context

def encrypt_data(context, data):
    encrypted_data = ts.ckks_vector(context, data)
    return encrypted_data

def decrypt_data(encrypted_data, secret_key):
    return encrypted_data.decrypt(secret_key=secret_key)

if __name__ == "__main__":

    # Contexto Original, com todos os valores.
    context = create_context()
    context2 = create_context()

    # Salvando Apenas Chave Pública, para "Transferência"
    context_serialized = context.serialize(save_public_key=True, save_secret_key=False)

    # Contexto Reconstruído em outro local.
    reconstructed_context = ts.Context.load(context_serialized)

    data_to_encrypt = [3.14, 2.71, 1.41]

    encrypted_data = encrypt_data(reconstructed_context, data_to_encrypt)

    # Passo 01 - Re-estruturar a Chave Pública do Contexto Original (no Broker) e o que veio na mensagem (do Cliente)
    pubKey_broker = context.serialize(save_public_key=True, save_secret_key=False)
    pubKey_message = encrypted_data.context().serialize(save_public_key=True, save_secret_key=False)

    if pubKey_broker == pubKey_message:
        print("Esses dados foram encriptados com essa chave pública.")
    else:
        print("Esses dados foram encriptados com outra chave!")

    # Testando com outro contexto
    pubKey_other_broker = context2.serialize(save_public_key=True, save_secret_key=False)
    pubKey_message = encrypted_data.context().serialize(save_public_key=True, save_secret_key=False)

    if pubKey_other_broker == pubKey_message:
        print("Esses dados foram encriptados com essa chave pública.")
    else:
        print("Esses dados foram encriptados com outra chave!")


    # Passo 02 - Com o contexto verificado, é possível passar a chave privada para decriptação.
    decrypted_data = decrypt_data(encrypted_data, secret_key = context.secret_key())
    
    print("Dados Descriptografados.", decrypted_data)