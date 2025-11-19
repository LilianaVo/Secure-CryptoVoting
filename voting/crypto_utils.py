from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

# ---------------------------------------------------------
# CONFIGURACIÓN AES (Confidencialidad - El "Candado")
# ---------------------------------------------------------
# Generamos una clave secreta aleatoria.
# Piensa en esto como la llave única de un candado que usaremos para cerrar los votos.
AES_KEY = get_random_bytes(32) 
BLOCK_SIZE = AES.block_size

def encrypt_vote_aes(vote_content):
    """
    Cifra el contenido del voto con AES-256 en modo CBC.
    Objetivo: Que nadie pueda leer el voto a simple vista (Confidencialidad).
    """
    # Preparamos el cifrador con nuestra llave maestra
    cipher = AES.new(AES_KEY, AES.MODE_CBC)
    
    # 1. Rellenamos el texto (pad) para que tenga el tamaño correcto.
    # 2. Lo encriptamos (lo convertimos en ruido ilegible).
    ciphertext_bytes = cipher.encrypt(pad(vote_content.encode('utf-8'), BLOCK_SIZE))
    
    # Retornamos dos cosas pegadas:
    # - IV (Vector de Inicialización): Un número aleatorio necesario para abrir el candado después.
    # - Ciphertext: El voto ya encriptado.
    return cipher.iv.hex() + ciphertext_bytes.hex()

# ---------------------------------------------------------
# FUNCIONES RSA (Autenticación - La "Firma Digital")
# ---------------------------------------------------------

def generate_rsa_keys():
    """
    Genera un par de llaves RSA de 2048 bits.
    Esto crea la identidad digital del votante.
    """
    # Creamos las llaves matemáticamente
    key = RSA.generate(2048)
    
    # Exportamos la PRIVADA (Secreto del usuario, usada para firmar)
    private_key_pem = key.export_key('PEM')
    
    # Exportamos la PÚBLICA (Visible para el sistema, usada para verificar)
    public_key_pem = key.publickey().export_key('PEM')

    return public_key_pem.decode('utf-8'), private_key_pem.decode('utf-8')

def sign_vote(vote_content, private_key_pem):
    """
    Firma el voto digitalmente.
    Objetivo: Garantizar que el voto vino de este usuario y no fue modificado (No Repudio).
    """
    try:
        # 1. Cargamos la llave privada del usuario (su "bolígrafo" digital)
        private_key = RSA.import_key(private_key_pem)
        
        # 2. Creamos un HASH (una huella digital única) del contenido del voto.
        # Si el voto cambia aunque sea una letra, este hash cambia totalmente.
        h = SHA256.new(vote_content.encode('utf-8'))
        
        # 3. Firmamos ese hash con la llave privada.
        signer = pkcs1_15.new(private_key)
        signature = signer.sign(h)
        
        return signature.hex()
    
    except ValueError as e:
        raise ValueError("Error al cargar o usar la llave privada. Asegúrese de que el archivo es correcto.") from e

def verify_signature(vote_content, signature_hex, public_key_pem):
    """
    Verifica la firma.
    Objetivo: El sistema comprueba si la firma es válida usando la llave pública.
    """
    try:
        # 1. Cargamos la Llave Pública del votante (que tenemos guardada en la BD)
        public_key = RSA.import_key(public_key_pem)

        # 2. Volvemos a calcular el Hash del voto que estamos viendo
        h = SHA256.new(vote_content.encode('utf-8'))
        
        # 3. Convertimos la firma que recibimos de hexadecimal a bytes reales
        signature = bytes.fromhex(signature_hex)

        # 4. El momento de la verdad:
        # Comparamos el hash del voto actual con la firma descifrada.
        # Si coinciden, es auténtico. Si no, alguien manipuló el voto.
        verifier = pkcs1_15.new(public_key)
        verifier.verify(h, signature)
        
        return True # ¡Firma válida!

    except (ValueError, TypeError):
        return False # Firma inválida o corrupta