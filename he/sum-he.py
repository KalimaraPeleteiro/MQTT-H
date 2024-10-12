"Testando o uso do Tenseal em um caso de Soma Simples."
import tenseal as ts

def create_context():
    context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=4096, plain_modulus=256)
    context.global_scale = 2 ** 40  
    return context

def encrypt_number(context, num):
    return ts.ckks_vector(context, [num])

def homomorphic_addition(enc_a, enc_b):
    return enc_a + enc_b

def decrypt_result(enc_result):
    return enc_result.decrypt()[0] 

context = create_context()

num1 = 67
num2 = 103
enc_num1 = encrypt_number(context, num1)
enc_num2 = encrypt_number(context, num2)

enc_sum = homomorphic_addition(enc_num1, enc_num2)

result = decrypt_result(enc_sum)
print(f"A soma de {num1} e {num2} é {result}.")
