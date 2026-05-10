from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

load_dotenv("security/.env")

# Get encryption key from .env
# If it doesn't exist yet, generate one automatically
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY:
    # Auto generate a key and print it so you can save it in .env
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print(f"[IMPORTANT] Add this to your .env file:")
    print(f"ENCRYPTION_KEY={ENCRYPTION_KEY}")

fernet = Fernet(ENCRYPTION_KEY.encode())


def encrypt_value(value: str) -> str:
    """Encrypts a string value — used for sensitive data like credit score"""
    return fernet.encrypt(value.encode()).decode()


def decrypt_value(encrypted_value: str) -> str:
    """Decrypts an encrypted value back to original"""
    return fernet.decrypt(encrypted_value.encode()).decode()
