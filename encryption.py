from cryptography.fernet import Fernet
import os

class Encryptor:
    def __init__(self, key_path='src/encryption.key'):
        """Initialize the encryptor with a key from file or generate a new one."""
        self.key_path = key_path
        
        os.makedirs(os.path.dirname(key_path), exist_ok=True)
        
        if not os.path.exists(key_path):
            self.key = Fernet.generate_key()
            with open(key_path, 'wb') as key_file:
                key_file.write(self.key)
        else:
            with open(key_path, 'rb') as key_file:
                self.key = key_file.read()
        
        self.cipher = Fernet(self.key)
    
    def encrypt(self, data):
        """Encrypt string or bytes data."""
        if isinstance(data, str):
            return self.cipher.encrypt(data.encode())
        return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data):
        """Decrypt bytes to bytes."""
        return self.cipher.decrypt(encrypted_data)
    
    def decrypt_to_string(self, encrypted_data):
        """Decrypt bytes to string."""
        return self.cipher.decrypt(encrypted_data).decode()