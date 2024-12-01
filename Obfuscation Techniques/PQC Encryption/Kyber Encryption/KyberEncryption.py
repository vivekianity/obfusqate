import argparse
import logging
import os
import hashlib
import base64
from typing import Tuple
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import HKDF
from Crypto.Hash import SHA256
from pqcrypto.kem.kyber512 import generate_keypair, encrypt, decrypt

# Configure logging
logger = logging.getLogger(__name__)

# ====================
# Constants
# ====================
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
AES_KEY_SIZE = 32  # 256 bits
NONCE_SIZE = 12  # 96 bits for GCM

# ====================
# Kyber KEM Functions
# ====================

def generate_kyber_keypair() -> Tuple[bytes, bytes]:
    """
    Generates a Kyber public and private key pair.

    Returns:
        Tuple[bytes, bytes]: The public key and private key.
    """
    public_key, private_key = generate_keypair()
    logger.debug("Kyber key pair generated.")
    return public_key, private_key

def encapsulate_kyber_key(public_key: bytes) -> Tuple[bytes, bytes]:
    """
    Encapsulates a shared secret using the Kyber public key.

    Args:
        public_key (bytes): The Kyber public key.

    Returns:
        Tuple[bytes, bytes]: The ciphertext and the shared secret.
    """
    ciphertext, shared_secret = encrypt(public_key)
    logger.debug("Shared secret encapsulated.")
    return ciphertext, shared_secret

def decapsulate_kyber_key(ciphertext: bytes, private_key: bytes) -> bytes:
    """
    Decapsulates the shared secret using the Kyber private key.

    Args:
        ciphertext (bytes): The Kyber ciphertext.
        private_key (bytes): The Kyber private key.

    Returns:
        bytes: The shared secret.
    """
    shared_secret = decrypt(private_key, ciphertext)
    logger.debug("Shared secret decapsulated.")
    return shared_secret

# ====================
# AES Encryption Functions
# ====================

def load_file_data(filename: str) -> bytes:
    """
    Loads data from a file.

    Args:
        filename (str): The path to the file.

    Returns:
        bytes: The file data.
    """
    with open(filename, 'rb') as file:
        data = file.read()
    logger.debug(f"Data loaded from {filename}.")
    return data

def encrypt_data(data: bytes, key: bytes, nonce_counter: int, original_filename: str, salt: bytes) -> bytes:
    """
    Encrypts data using AES-256 in GCM mode with a unique nonce and includes the original filename.

    Args:
        data (bytes): The plaintext data.
        key (bytes): The AES-256 key (32 bytes).
        nonce_counter (int): A counter to generate a unique nonce.
        original_filename (str): The original filename to include in the encrypted data.
        salt (bytes): The salt used in HKDF.

    Returns:
        bytes: The encrypted data including salt, nonce, tag, and original filename.
    """
    # Prepare data with filename
    filename_bytes = original_filename.encode('utf-8')
    filename_length = len(filename_bytes)
    filename_length_bytes = filename_length.to_bytes(2, 'big')  # 2 bytes for filename length
    data_to_encrypt = filename_length_bytes + filename_bytes + data

    # Encrypt as before
    nonce = os.urandom(NONCE_SIZE)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(data_to_encrypt)

    # Include the salt at the beginning of the encrypted data
    encrypted_data = salt + nonce + tag + ciphertext  # CHANGED
    logger.debug("Data encrypted using AES-256 GCM with original filename and salt included.")
    return encrypted_data

def decrypt_data(encrypted_data: bytes, key: bytes) -> Tuple[bytes, str]:
    """
    Decrypts data encrypted with AES-256 in GCM mode and extracts the original filename.

    Args:
        encrypted_data (bytes): The encrypted data including nonce and tag.
        key (bytes): The AES-256 key (32 bytes).

    Returns:
        Tuple[bytes, str]: The decrypted plaintext data and the original filename.
    """
    # Extract the nonce, tag, and ciphertext
    nonce = encrypted_data[:NONCE_SIZE]
    tag = encrypted_data[NONCE_SIZE:NONCE_SIZE + 16]
    ciphertext = encrypted_data[NONCE_SIZE + 16:]
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    logger.debug("Data decrypted using AES-256 GCM.")

    # Extract original filename
    filename_length = int.from_bytes(data[:2], 'big')
    filename_bytes = data[2:2+filename_length]
    original_filename = filename_bytes.decode('utf-8')
    file_data = data[2+filename_length:]
    logger.debug(f"Original filename extracted: {original_filename}")
    return file_data, original_filename

# ====================
# File Handling Functions
# ====================

def save_to_file(data: bytes, filename: str) -> None:
    """
    Saves binary data to a file.

    Args:
        data (bytes): The data to save.
        filename (str): The path to the file.
    """
    with open(filename, 'wb') as file:
        file.write(data)
    logger.debug(f"Data saved to {filename}.")

def compute_hash(data: bytes) -> str:
    """
    Computes SHA-256 hash of the given data.

    Args:
        data (bytes): The data to hash.

    Returns:
        str: The hexadecimal representation of the hash.
    """
    return hashlib.sha256(data).hexdigest()

def save_private_key(private_key: bytes, filename: str) -> None:
    """
    Saves the Kyber private key to a file with restricted permissions using Base64 encoding.

    Args:
        private_key (bytes): The private key data.
        filename (str): The path to the file.
    """
    encoded_key = base64.b64encode(private_key)
    with open(filename, 'wb') as file:
        file.write(encoded_key)
    os.chmod(filename, 0o600)  # Owner can read and write
    logger.debug(f"Private key saved to {filename} with restricted permissions.")

    # Compute and log hash of the private key
    private_key_hash = compute_hash(private_key)
    logger.debug(f"Private key hash (before saving): {private_key_hash}")

def load_private_key(filename: str) -> bytes:
    """
    Loads the Kyber private key from a Base64-encoded file.

    Args:
        filename (str): The path to the file.

    Returns:
        bytes: The private key data.
    """
    with open(filename, 'rb') as file:
        encoded_key = file.read()
    private_key = base64.b64decode(encoded_key)
    logger.debug(f"Private key loaded from {filename}.")

    # Compute and log hash of the private key
    private_key_hash_loaded = compute_hash(private_key)
    logger.debug(f"Private key hash (after loading): {private_key_hash_loaded}")

    return private_key

def save_public_key(public_key: bytes, filename: str) -> None:
    """
    Saves the Kyber public key to a file using Base64 encoding.

    Args:
        public_key (bytes): The public key data.
        filename (str): The path to the file.
    """
    encoded_key = base64.b64encode(public_key)
    with open(filename, 'wb') as file:
        file.write(encoded_key)
    logger.debug(f"Public key saved to {filename}.")

    # Compute and log hash of the public key
    public_key_hash = compute_hash(public_key)
    logger.debug(f"Public key hash (before saving): {public_key_hash}")

def load_public_key(filename: str) -> bytes:
    """
    Loads the Kyber public key from a Base64-encoded file.

    Args:
        filename (str): The path to the file.

    Returns:
        bytes: The public key data.
    """
    with open(filename, 'rb') as file:
        encoded_key = file.read()
    public_key = base64.b64decode(encoded_key)
    logger.debug(f"Public key loaded from {filename}.")

    # Compute and log hash of the public key
    public_key_hash_loaded = compute_hash(public_key)
    logger.debug(f"Public key hash (after loading): {public_key_hash_loaded}")

    return public_key

# ====================
# Main Interactive Functions
# ====================

def generate_key_pair() -> None:
    """
    Generates a Kyber public and private key pair with user-specified name and saves them to files.
    """
    # Prompt user for a name
    while True:
        name = input("Enter a name to prefix your key files (e.g., 'alice', 'jak'): ").strip()
        if not name:
            print("Name cannot be empty. Please enter a valid name.")
            continue
        if any(c in name for c in r'\/:*?"<>|'):
            print("Name contains invalid characters. Please avoid characters like \\ / : * ? \" < > |")
            continue
        break

    public_key_file = f"{name}_kyber_public_key.bin"
    private_key_file = f"{name}_kyber_private_key.bin"

    # Check if key files already exist
    if (os.path.exists(public_key_file) or os.path.exists(private_key_file)):
        overwrite_input = input(f"Key files '{public_key_file}' or '{private_key_file}' already exist. Do you want to overwrite them? (yes/no): ").strip().lower()
        if overwrite_input not in ['yes', 'y']:
            print("Key generation aborted.\n")
            return

    # Generate Kyber keys
    public_key, private_key = generate_kyber_keypair()
    save_public_key(public_key, public_key_file)
    save_private_key(private_key, private_key_file)
    logger.info(f"Kyber public key saved to '{public_key_file}'.")
    logger.info(f"Kyber private key saved to '{private_key_file}'.")

    print("\n=== Key Pair Generation Successful ===")
    print(f"Public Key File: {public_key_file}")
    print(f"Private Key File: {private_key_file}")
    print("\nPlease share your public key file with the recipient securely.")
    print("Ensure that you keep your private key file confidential.\n")

def encrypt_file_interactive() -> None:
    """
    Interactive function to encrypt a file for a recipient using their public key.
    """
    # Prompt for the user's private key file name
    private_key_file = input("Enter your private key file name (e.g., 'jak_kyber_private_key.bin'): ").strip()
    if not os.path.exists(private_key_file):
        print(f"Private key file '{private_key_file}' not found. Generate your key pair first.")
        return

    # Prompt for the recipient's public key file name
    recipient_public_key_file = input("Enter the recipient's public key file name (e.g., 'alice_kyber_public_key.bin'): ").strip()
    if not os.path.exists(recipient_public_key_file):
        print(f"Recipient's public key file '{recipient_public_key_file}' does not exist.")
        return

    # Prompt for the file to encrypt
    input_file = input("Enter the file name you want to encrypt (e.g., 'document.txt'): ").strip()
    if not os.path.exists(input_file):
        print(f"Input file '{input_file}' does not exist.")
        return

    # Check file size
    file_size = os.path.getsize(input_file)
    if file_size > MAX_FILE_SIZE:
        print(f"File size exceeds the maximum allowed size of {MAX_FILE_SIZE} bytes.")
        return

    # Define output files
    encrypted_file = f"{input_file}.enc"
    encapsulated_key_file = f"{input_file}.enc.key"

    # Load recipient's public key
    try:
        public_key = load_public_key(recipient_public_key_file)
    except Exception as e:
        print(f"Failed to load recipient's public key: {e}")
        return

    # Encapsulate shared secret
    ciphertext, shared_secret = encapsulate_kyber_key(public_key)
    save_to_file(ciphertext, encapsulated_key_file)
    logger.info(f"Kyber encapsulated key saved to '{encapsulated_key_file}'.")

    # Generate a random salt
    salt = os.urandom(16)  # 16 bytes of random data

    # Derive AES-256 key using HKDF with salt
    try:
        aes_key = HKDF(master=shared_secret, key_len=AES_KEY_SIZE, salt=salt, hashmod=SHA256)  # CHANGED
        logger.debug("AES-256 Key derived with salt.")
    except TypeError as e:
        logger.error(f"HKDF() error: {e}")
        print("Encryption failed due to a key derivation error.")
        return

    # Load input data
    try:
        data = load_file_data(input_file)
        logger.info(f"Input file '{input_file}' loaded.")
    except Exception as e:
        print(f"Failed to load input file: {e}")
        return

    # Encrypt data
    encrypted_data = encrypt_data(data, aes_key, nonce_counter=1, original_filename=input_file, salt=salt)
    save_to_file(encrypted_data, encrypted_file)
    logger.info(f"Encrypted data saved to '{encrypted_file}'.")

    # Inform the user about the files to send
    print("\n=== Encryption Successful ===")
    print(f"Encrypted File: {encrypted_file}")
    print(f"Encapsulated Key File: {encapsulated_key_file}")
    print("\nTo allow the recipient to decrypt the file, send them the following files securely:")
    print(f"- Encrypted File: {encrypted_file}")
    print(f"- Encapsulated Key File: {encapsulated_key_file}")
    print(f"\nDO NOT share your private key file: {private_key_file}\n")

def decrypt_file_interactive() -> None:
    """
    Interactive function to decrypt a received encrypted file using the user's private key.
    """
    # Prompt for the user's private key file name
    private_key_file = input("Enter your private key file name (e.g., 'alice_kyber_private_key.bin'): ").strip()
    if not os.path.exists(private_key_file):
        print(f"Private key file '{private_key_file}' not found. Generate your key pair first.")
        return

    # Prompt for the encrypted file name
    encrypted_file = input("Enter the encrypted file name (e.g., 'document.txt.enc'): ").strip()
    if not os.path.exists(encrypted_file):
        print(f"Encrypted file '{encrypted_file}' does not exist.")
        return

    # Prompt for the encapsulated key file name
    encapsulated_key_file = input("Enter the encapsulated key file name (e.g., 'document.txt.enc.key'): ").strip()
    if not os.path.exists(encapsulated_key_file):
        print(f"Encapsulated key file '{encapsulated_key_file}' does not exist.")
        return

    # Load user's private key
    try:
        private_key = load_private_key(private_key_file)
    except Exception as e:
        print(f"Failed to load your private key: {e}")
        return

    # Load encapsulated key (ciphertext)
    try:
        ciphertext = load_file_data(encapsulated_key_file)
        logger.info(f"Kyber encapsulated key loaded from '{encapsulated_key_file}'.")
    except Exception as e:
        print(f"Failed to load encapsulated key file: {e}")
        return

    # Decapsulate shared secret
    try:
        shared_secret = decapsulate_kyber_key(ciphertext, private_key)
    except Exception as e:
        print(f"Failed to decapsulate the shared secret: {e}")
        return

    # Load encrypted data
    try:
        encrypted_data = load_file_data(encrypted_file)
        logger.info(f"Encrypted file '{encrypted_file}' loaded.")
    except Exception as e:
        print(f"Failed to load encrypted file: {e}")
        return

    # Extract the salt from the beginning of the encrypted data
    salt = encrypted_data[:16]  # CHANGED
    encrypted_data = encrypted_data[16:]  # CHANGED

    # Derive AES-256 key using HKDF with the extracted salt
    try:
        aes_key = HKDF(master=shared_secret, key_len=AES_KEY_SIZE, salt=salt, hashmod=SHA256)
        logger.debug("AES-256 Key derived using extracted salt.")
    except TypeError as e:
        logger.error(f"HKDF() error: {e}")
        print("Decryption failed due to a key derivation error.")
        return

    # Decrypt data and extract original filename
    try:
        data, original_filename = decrypt_data(encrypted_data, aes_key)
    except Exception as e:
        print(f"Failed to decrypt the data: {e}")
        return

    # Sanitize the original filename
    safe_filename = os.path.basename(original_filename)

    # Check if file exists
    if os.path.exists(safe_filename):
        overwrite_input = input(f"File '{safe_filename}' already exists. Do you want to overwrite it? (yes/no): ").strip().lower()
        if overwrite_input not in ['yes', 'y']:
            print("Decryption aborted.")
            return

    # Save decrypted data
    try:
        save_to_file(data, safe_filename)
        logger.info(f"Decrypted data saved to '{safe_filename}'.")
    except Exception as e:
        print(f"Failed to save decrypted data: {e}")
        return

    print("\n=== Decryption Successful ===")
    print(f"Decrypted File: {safe_filename}\n")

# ====================
# Argument Parser Setup
# ====================

def main():
    parser = argparse.ArgumentParser(description="Kyber KEM-based File Encryption and Decryption Tool")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    # Set up logging level
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')

    while True:
        print("=== Kyber KEM File Encryption Tool ===")
        print("Select an option:")
        print("1. Generate Kyber Key Pair")
        print("2. Encrypt a File")
        print("3. Decrypt a File")
        print("4. Exit")

        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            generate_key_pair()
        elif choice == '2':
            encrypt_file_interactive()
        elif choice == '3':
            decrypt_file_interactive()
        elif choice == '4':
            print("Exiting the tool. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 4.\n")

if __name__ == "__main__":
    main()