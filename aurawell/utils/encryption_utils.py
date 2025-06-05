"""
Encryption Utilities

This module provides utilities for encrypting and decrypting sensitive data,
particularly health information and user credentials.
"""

import base64
import hashlib
import secrets
from typing import Union, Tuple, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """
    Manager for encryption and decryption operations
    """
    
    def __init__(self, password: Optional[str] = None):
        """
        Initialize encryption manager
        
        Args:
            password: Optional password for key derivation
        """
        self.fernet = None
        if password:
            self.set_password(password)
    
    def set_password(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """
        Set password for encryption/decryption
        
        Args:
            password: Password string
            salt: Optional salt (will generate if not provided)
            
        Returns:
            The salt used
        """
        if salt is None:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        self.fernet = Fernet(key)
        
        return salt
    
    def encrypt(self, data: Union[str, bytes]) -> bytes:
        """
        Encrypt data
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data
            
        Raises:
            ValueError: If encryption manager not initialized
        """
        if self.fernet is None:
            raise ValueError("Encryption manager not initialized with password")
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        return self.fernet.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data
        
        Args:
            encrypted_data: Encrypted data
            
        Returns:
            Decrypted data
            
        Raises:
            ValueError: If encryption manager not initialized
        """
        if self.fernet is None:
            raise ValueError("Encryption manager not initialized with password")
        
        return self.fernet.decrypt(encrypted_data)
    
    def encrypt_string(self, text: str) -> str:
        """
        Encrypt string and return base64 encoded result
        
        Args:
            text: Text to encrypt
            
        Returns:
            Base64 encoded encrypted text
        """
        encrypted_bytes = self.encrypt(text)
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """
        Decrypt base64 encoded encrypted string
        
        Args:
            encrypted_text: Base64 encoded encrypted text
            
        Returns:
            Decrypted text
        """
        encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
        decrypted_bytes = self.decrypt(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token
    
    Args:
        length: Length of the token in bytes
        
    Returns:
        Secure random token as hex string
    """
    return secrets.token_hex(length)


def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, str]:
    """
    Hash password with salt using PBKDF2
    
    Args:
        password: Password to hash
        salt: Optional salt (will generate if not provided)
        
    Returns:
        Tuple of (hashed_password, salt) as hex strings
    """
    if salt is None:
        salt = secrets.token_bytes(32)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    hashed = kdf.derive(password.encode('utf-8'))
    
    return hashed.hex(), salt.hex()


def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    """
    Verify password against hash
    
    Args:
        password: Plain text password
        hashed_password: Hashed password (hex string)
        salt: Salt (hex string)
        
    Returns:
        True if password matches
    """
    try:
        salt_bytes = bytes.fromhex(salt)
        expected_hash = bytes.fromhex(hashed_password)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt_bytes,
            iterations=100000,
        )
        
        # This will raise an exception if passwords don't match
        kdf.verify(password.encode('utf-8'), expected_hash)
        return True
    except Exception:
        return False


def hash_sensitive_data(data: str) -> str:
    """
    Hash sensitive data using SHA-256 (one-way hash)
    
    Args:
        data: Data to hash
        
    Returns:
        SHA-256 hash as hex string
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest()


def generate_api_key() -> str:
    """
    Generate a secure API key
    
    Returns:
        API key string
    """
    return f"ak_{generate_secure_token(24)}"


def obfuscate_sensitive_string(sensitive_string: str, show_chars: int = 4) -> str:
    """
    Obfuscate sensitive string for logging/display
    
    Args:
        sensitive_string: String to obfuscate
        show_chars: Number of characters to show at start/end
        
    Returns:
        Obfuscated string
    """
    if len(sensitive_string) <= show_chars * 2:
        return "*" * len(sensitive_string)
    
    start = sensitive_string[:show_chars]
    end = sensitive_string[-show_chars:]
    middle = "*" * (len(sensitive_string) - show_chars * 2)
    
    return f"{start}{middle}{end}"


def secure_compare(a: str, b: str) -> bool:
    """
    Securely compare two strings to prevent timing attacks
    
    Args:
        a: First string
        b: Second string
        
    Returns:
        True if strings are equal
    """
    return secrets.compare_digest(a, b)


class SecureDataContainer:
    """
    Container for securely storing sensitive data in memory
    """
    
    def __init__(self, encryption_manager: EncryptionManager):
        """
        Initialize secure container
        
        Args:
            encryption_manager: Encryption manager instance
        """
        self.encryption_manager = encryption_manager
        self._data = {}
    
    def store(self, key: str, value: str) -> None:
        """
        Store data securely
        
        Args:
            key: Key for the data
            value: Value to store
        """
        encrypted_value = self.encryption_manager.encrypt_string(value)
        self._data[key] = encrypted_value
        logger.debug(f"Stored encrypted data for key: {key}")
    
    def retrieve(self, key: str) -> Optional[str]:
        """
        Retrieve and decrypt data
        
        Args:
            key: Key for the data
            
        Returns:
            Decrypted value or None if not found
        """
        encrypted_value = self._data.get(key)
        if encrypted_value is None:
            return None
        
        try:
            return self.encryption_manager.decrypt_string(encrypted_value)
        except Exception as e:
            logger.error(f"Failed to decrypt data for key {key}: {e}")
            return None
    
    def remove(self, key: str) -> bool:
        """
        Remove data from container
        
        Args:
            key: Key to remove
            
        Returns:
            True if key was found and removed
        """
        if key in self._data:
            del self._data[key]
            logger.debug(f"Removed data for key: {key}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all data from container"""
        self._data.clear()
        logger.debug("Cleared all data from secure container")
    
    def keys(self) -> list:
        """Get list of keys (for debugging - doesn't expose values)"""
        return list(self._data.keys())


def encrypt_health_data(data: dict, encryption_key: str) -> str:
    """
    Encrypt health data dictionary
    
    Args:
        data: Health data dictionary
        encryption_key: Encryption key
        
    Returns:
        Encrypted data as base64 string
    """
    import json
    
    # Convert dict to JSON string
    json_data = json.dumps(data, ensure_ascii=False)
    
    # Create encryption manager
    manager = EncryptionManager()
    manager.set_password(encryption_key)
    
    # Encrypt and return
    return manager.encrypt_string(json_data)


def decrypt_health_data(encrypted_data: str, encryption_key: str) -> dict:
    """
    Decrypt health data
    
    Args:
        encrypted_data: Encrypted data as base64 string
        encryption_key: Encryption key
        
    Returns:
        Decrypted data dictionary
        
    Raises:
        ValueError: If decryption fails
    """
    import json
    
    try:
        # Create encryption manager
        manager = EncryptionManager()
        manager.set_password(encryption_key)
        
        # Decrypt
        json_data = manager.decrypt_string(encrypted_data)
        
        # Parse JSON
        return json.loads(json_data)
        
    except Exception as e:
        raise ValueError(f"Failed to decrypt health data: {e}")


# Global encryption manager instance (initialize with environment variable)
_global_encryption_manager = None


def get_global_encryption_manager() -> Optional[EncryptionManager]:
    """
    Get global encryption manager instance
    
    Returns:
        Global encryption manager or None if not initialized
    """
    global _global_encryption_manager
    return _global_encryption_manager


def initialize_global_encryption(password: str) -> None:
    """
    Initialize global encryption manager
    
    Args:
        password: Master password for encryption
    """
    global _global_encryption_manager
    _global_encryption_manager = EncryptionManager(password)
    logger.info("Global encryption manager initialized")


def cleanup_global_encryption() -> None:
    """Cleanup global encryption manager"""
    global _global_encryption_manager
    _global_encryption_manager = None
    logger.info("Global encryption manager cleaned up") 