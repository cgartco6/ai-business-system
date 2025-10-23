import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt
from datetime import datetime, timedelta
import hashlib

class MilitaryGradeSecurity:
    def __init__(self):
        self.master_key = self._derive_key()
        self.cipher_suite = Fernet(self.master_key)
        
    def _derive_key(self):
        # Use environment variable for salt in production
        salt = b'costbyte_military_grade_salt_2024'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=1000000,  # High iteration count for security
        )
        key = base64.urlsafe_b64encode(kdf.derive(b"costbyte_master_key_2024"))
        return key
    
    def encrypt_data(self, data):
        """Encrypt sensitive data"""
        if isinstance(data, str):
            data = data.encode()
        encrypted_data = self.cipher_suite.encrypt(data)
        return base64.urlsafe_b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data):
        """Decrypt sensitive data"""
        encrypted_data = base64.urlsafe_b64decode(encrypted_data.encode())
        return self.cipher_suite.decrypt(encrypted_data).decode()
    
    def create_access_token(self, user_id, permissions):
        """Create JWT access token"""
        payload = {
            'user_id': user_id,
            'permissions': permissions,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.master_key, algorithm='HS256')
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.master_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

class APISecurity:
    def __init__(self):
        self.allowed_ips = self._load_whitelist()
        self.rate_limits = {}
    
    def _load_whitelist(self):
        """Load whitelisted IP addresses"""
        return ['127.0.0.1', '192.168.1.0/24']  # Add production IPs
    
    def check_ip_access(self, ip_address):
        """Check if IP is whitelisted"""
        for allowed_ip in self.allowed_ips:
            if ip_address.startswith(allowed_ip.split('/')[0]):
                return True
        return False
    
    def check_rate_limit(self, api_key, max_requests=1000):
        """Implement rate limiting"""
        current_minute = datetime.now().strftime('%Y-%m-%d %H:%M')
        key = f"{api_key}_{current_minute}"
        
        if key not in self.rate_limits:
            self.rate_limits[key] = 0
        
        self.rate_limits[key] += 1
        return self.rate_limits[key] <= max_requests
