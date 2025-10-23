import logging
from datetime import datetime, timedelta
import jwt
from functools import wraps

class AccessControl:
    def __init__(self, secret_key):
        self.secret_key = secret_key
        self.failed_attempts = {}
        self.lockout_time = timedelta(minutes=30)
        
    def create_session_token(self, user_id, role, permissions):
        """Create JWT session token with role-based permissions"""
        payload = {
            'user_id': user_id,
            'role': role,
            'permissions': permissions,
            'exp': datetime.utcnow() + timedelta(hours=12),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_session(self, token):
        """Verify session token and return user context"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def check_permission(self, user_context, required_permission):
        """Check if user has required permission"""
        if not user_context:
            return False
        return required_permission in user_context.get('permissions', [])
    
    def log_access_attempt(self, ip_address, success=True):
        """Log access attempts and implement lockout"""
        if ip_address not in self.failed_attempts:
            self.failed_attempts[ip_address] = {'count': 0, 'lockout_until': None}
        
        if not success:
            self.failed_attempts[ip_address]['count'] += 1
            
            # Implement lockout after 5 failed attempts
            if self.failed_attempts[ip_address]['count'] >= 5:
                self.failed_attempts[ip_address]['lockout_until'] = datetime.utcnow() + self.lockout_time
                logging.warning(f"IP {ip_address} locked out for 30 minutes")
        
        return success
    
    def is_ip_locked_out(self, ip_address):
        """Check if IP is currently locked out"""
        if ip_address in self.failed_attempts:
            lockout_until = self.failed_attempts[ip_address].get('lockout_until')
            if lockout_until and datetime.utcnow() < lockout_until:
                return True
        return False

def require_permission(permission):
    """Decorator for requiring specific permissions"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This would be integrated with web framework
            token = kwargs.get('token')
            access_control = kwargs.get('access_control')
            
            if not token or not access_control:
                return {"error": "Authentication required"}, 401
            
            user_context = access_control.verify_session(token)
            if not user_context or not access_control.check_permission(user_context, permission):
                return {"error": "Insufficient permissions"}, 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
