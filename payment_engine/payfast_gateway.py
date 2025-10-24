import logging
import hashlib
import hmac
import urllib.parse
from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional
import requests

class PayFastGateway:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
        self.base_url = "https://www.payfast.co.za/eng/process" if self.config['live_mode'] else "https://sandbox.payfast.co.za/eng/process"
    
    def _load_config(self) -> Dict:
        """Load PayFast configuration"""
        # In production, these would be encrypted and from environment variables
        return {
            'merchant_id': '10000100',  # Example sandbox ID
            'merchant_key': '46f0cd694581a',
            'passphrase': 'testpassphrase',
            'live_mode': False,  # Set to True for production
            'return_url': 'https://yourdomain.com/payment/success',
            'cancel_url': 'https://yourdomain.com/payment/cancel',
            'notify_url': 'https://yourdomain.com/webhook/payfast'
        }
    
    def create_payment_request(self, amount: Decimal, payment_data: Dict) -> Dict:
        """Create PayFast payment request"""
        try:
            # Prepare payment data
            data = {
                'merchant_id': self.config['merchant_id'],
                'merchant_key': self.config['merchant_key'],
                'return_url': payment_data.get('return_url', self.config['return_url']),
                'cancel_url': payment_data.get('cancel_url', self.config['cancel_url']),
                'notify_url': payment_data.get('notify_url', self.config['notify_url']),
                'name_first': payment_data.get('first_name', ''),
                'name_last': payment_data.get('last_name', ''),
                'email_address': payment_data.get('email', ''),
                'm_payment_id': payment_data.get('payment_reference', ''),
                'amount': str(amount),
                'item_name': payment_data.get('description', 'CostByte Service'),
                'item_description': payment_data.get('item_description', 'Monthly subscription'),
                'custom_int1': payment_data.get('client_id'),
                'custom_str1': payment_data.get('service_tier', 'professional')
            }
            
            # Remove empty values
            data = {k: v for k, v in data.items() if v}
            
            # Generate signature
            signature = self._generate_signature(data)
            data['signature'] = signature
            
            self.logger.info(f"Created PayFast payment request for amount: {amount}")
            
            return {
                'success': True,
                'payment_id': data.get('m_payment_id'),
                'gateway': 'payfast',
                'checkout_url': f"{self.base_url}?{urllib.parse.urlencode(data)}",
                'status': 'pending',
                'data': data
            }
            
        except Exception as e:
            self.logger.error(f"PayFast payment creation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'payfast'
            }
    
    def verify_webhook(self, payload: Dict, signature: str) -> bool:
        """Verify PayFast ITN (Instant Transaction Notification)"""
        try:
            # Verify signature
            calculated_signature = self._generate_signature(payload)
            if calculated_signature != signature:
                self.logger.warning("PayFast signature verification failed")
                return False
            
            # Verify payment status
            payment_status = payload.get('payment_status')
            if payment_status != 'COMPLETE':
                self.logger.warning(f"PayFast payment not complete: {payment_status}")
                return False
            
            # Verify amount (optional but recommended)
            expected_amount = payload.get('amount_gross')
            # You would compare this with your expected amount
            
            self.logger.info("PayFast webhook verified successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"PayFast webhook verification error: {e}")
            return False
    
    def get_payment_status(self, payment_id: str) -> Dict:
        """Get payment status from PayFast"""
        try:
            # PayFast doesn't have a direct status API, so we rely on ITN
            # For demo purposes, we'll return a mock response
            return {
                'success': True,
                'payment_id': payment_id,
                'status': 'completed',  # This would come from your database
                'gateway': 'payfast'
            }
            
        except Exception as e:
            self.logger.error(f"PayFast status check error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_signature(self, data: Dict) -> str:
        """Generate PayFast signature"""
        # Create parameter string
        param_string = '&'.join([
            f'{urllib.parse.quote_plus(str(k))}={urllib.parse.quote_plus(str(v))}'
            for k, v in sorted(data.items()) if v is not None
        ])
        
        # Add passphrase if set
        if self.config.get('passphrase'):
            param_string += f"&passphrase={urllib.parse.quote_plus(self.config['passphrase'])}"
        
        # Generate MD5 hash
        return hashlib.md5(param_string.encode()).hexdigest()
