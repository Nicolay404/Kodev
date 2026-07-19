import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def generate_keys():
    # El archivo asume que corre en samr/services/auth-service/scripts/
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    keys_dir = os.path.join(base_dir, 'keys')
    
    if not os.path.exists(keys_dir):
        os.makedirs(keys_dir)

    private_key_path = os.path.join(keys_dir, 'private.pem')
    public_key_path = os.path.join(keys_dir, 'public.pem')

    if os.path.exists(private_key_path) and os.path.exists(public_key_path):
        print(f"Las llaves ya existen en {keys_dir}")
        return

    # Generar clave privada 4096 bits
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
    )

    # Generar clave pública
    public_key = private_key.public_key()

    # Guardar clave privada
    with open(private_key_path, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))

    # Guardar clave pública
    with open(public_key_path, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))

    print(f"Claves RSA (RS256, 4096 bits) generadas exitosamente en {keys_dir}")

if __name__ == "__main__":
    generate_keys()
