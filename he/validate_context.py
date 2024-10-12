"""Estudando uma maneira de validar se um conteúdo encriptado pertence a um determinado contexto."""
import tenseal as ts

def create_context():
    context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=4096, plain_modulus=256)
    context.global_scale = 2 ** 40  
    return context

def encrypt_data(context, data):
    encrypted_data = ts.ckks_vector(context, data)
    return encrypted_data

def decrypt_data(encrypted_data):
    return encrypted_data.decrypt()

if __name__ == "__main__":
    context = create_context()
    context2 = create_context()

    data_to_encrypt = [3.14, 2.71, 1.41]

    encrypted_data = encrypt_data(context, data_to_encrypt)

    decrypted_data = decrypt_data(encrypted_data)
    
    print("Dados Descriptografados.", decrypted_data)


    # Para verificar se certos dados foram encriptografados por um determinado contexto, basta comparar
    # a propriedade "data". É possível acessar o contexto um CKSS Vector usando o método context().
    print("Comparando com o Contexto 01...")
    if encrypted_data.context().data == context.data:
        print("Esses dados foram encriptados com esse contexto.")
    else:
        print("Esses dados foram encriptados com outro contexto!")
    
    print("\nComparando com o Contexto 02...")
    if encrypted_data.context().data == context2.data:
        print("Esses dados foram encriptados com esse contexto.")
    else:
        print("Esses dados foram encriptados com outro contexto!")
