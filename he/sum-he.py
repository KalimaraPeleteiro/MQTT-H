import tenseal as ts

# Create a context for encryption
def create_context():
    context = ts.context(ts.SCHEME_TYPE.CKKS, poly_modulus_degree=4096, plain_modulus=256)
    context.global_scale = 2 ** 40  # Set a global scale
    return context

# Function to encrypt numbers
def encrypt_number(context, num):
    return ts.ckks_vector(context, [num])

# Function to perform homomorphic addition
def homomorphic_addition(enc_a, enc_b):
    return enc_a + enc_b

# Function to decrypt the result
def decrypt_result(enc_result):
    return enc_result.decrypt()[0]  # Get the first element since it's a vector

# Example usage
context = create_context()

# Encrypt the numbers
num1 = 67
num2 = 103
enc_num1 = encrypt_number(context, num1)
enc_num2 = encrypt_number(context, num2)

# Perform homomorphic addition
enc_sum = homomorphic_addition(enc_num1, enc_num2)

# Decrypt the result
result = decrypt_result(enc_sum)
print(f"The sum of {num1} and {num2} is {result}.")
