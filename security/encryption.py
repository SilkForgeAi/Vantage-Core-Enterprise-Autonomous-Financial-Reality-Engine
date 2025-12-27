"""API key encryption and decryption utilities."""
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
from typing import Optional
import os


class KeyEncryption:
    """Encrypt and decrypt sensitive API keys per user."""
    
    def __init__(self, master_key: str):
        """
        Initialize with a master encryption key.
        
        Args:
            master_key: 32-byte hex string (64 hex characters)
        """
        if len(master_key) != 64:
            raise ValueError("Master key must be 64 hex characters (32 bytes)")
        
        # Convert hex to bytes
        key_bytes = bytes.fromhex(master_key)
        
        # Use PBKDF2 to derive a key suitable for Fernet
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'stable_salt_for_trading_agent',  # In production, use per-user salts
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_bytes))
        
        self.cipher = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt a plaintext string."""
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt a ciphertext string."""
        return self.cipher.decrypt(ciphertext.encode()).decode()
    
    def encrypt_api_key(self, user_id: str, exchange: str, api_key: str, api_secret: str) -> dict:
        """
        Encrypt API credentials for a user.
        
        Returns:
            Dict with encrypted key and secret
        """
        return {
            "user_id": user_id,
            "exchange": exchange,
            "encrypted_api_key": self.encrypt(api_key),
            "encrypted_api_secret": self.encrypt(api_secret)
        }
    
    def decrypt_api_key(self, encrypted_key: str, encrypted_secret: str) -> tuple[str, str]:
        """
        Decrypt API credentials.
        
        Returns:
            Tuple of (api_key, api_secret)
        """
        return (
            self.decrypt(encrypted_key),
            self.decrypt(encrypted_secret)
        )


def generate_master_key() -> str:
    """Generate a random 32-byte hex key for encryption."""
    return os.urandom(32).hex()

