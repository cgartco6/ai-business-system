import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import hashlib

class EncryptionEngine:
    def __init__(self):
        self.master_key = self._generate_master_key()
        self.data_key = self._derive_data_key()
        
    def _generate_master_key(self):
        """Generate master encryption key"""
        # In production, this should be from secure environment variable
        return Fernet.generate_key()
    
    def _derive_data_key(self):
        """Derive data-specific encryption key"""
        password = b"costbyte_data_encryption_key_2024"
        salt = b"costbyte_salt_2024"
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password))
    
    def encrypt_sensitive_data(self, data, data_type):
        """Encrypt sensitive data with type-specific handling"""
        if data_type == "bank":
            cipher_suite = Fernet(self.master_key)
        else:
            cipher_suite = Fernet(self.data_key)
            
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        encrypted_data = cipher_suite.encrypt(data)
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_sensitive_data(self, encrypted_data, data_type):
        """Decrypt sensitive data"""
        if data_type == "bank":
            cipher_suite = Fernet(self.master_key)
        else:
            cipher_suite = Fernet(self.data_key)
            
        encrypted_data = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
        decrypted_data = cipher_suite.decrypt(encrypted_data)
        return decrypted_data.decode('utf-8')
    
    def hash_sensitive_info(self, data):
        """Create irreversible hash of sensitive information"""
        return hashlib.sha512(data.encode('utf-8')).hexdigest()

class SecureStorage:
    def __init__(self):
        self.encryption = EncryptionEngine()
        
    def store_client_data(self, client_info):
        """Securely store client information"""
        secure_data = {
            'name_hash': self.encryption.hash_sensitive_info(client_info['name']),
            'email_hash': self.encryption.hash_sensitive_info(client_info['email']),
            'encrypted_contact': self.encryption.encrypt_sensitive_data(
                client_info.get('phone', ''), 'contact'
            ),
            'encrypted_address': self.encryption.encrypt_sensitive_data(
                f"{client_info.get('address', '')} {client_info.get('city', '')}", 'location'
            )
        }
        return secure_data
    
    def store_bank_details(self, bank_info):
        """Securely store bank account information"""
        encrypted_bank_data = {
            'encrypted_account': self.encryption.encrypt_sensitive_data(
                bank_info['account_number'], 'bank'
            ),
            'encrypted_branch': self.encryption.encrypt_sensitive_data(
                bank_info['branch_code'], 'bank'
            ),
            'bank_name': bank_info['bank_name']  # Not encrypted for reporting
        }
        return encrypted_bank_data
