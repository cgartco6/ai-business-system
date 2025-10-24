import logging
from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional
import hashlib
import hmac
import json

class PaymentProcessor:
    def __init__(self, db_connection, encryption_engine):
        self.db = db_connection
        self.encryption = encryption_engine
        self.logger = logging.getLogger(__name__)
        
        # Initialize payment gateways
        self.payfast = PayFastGateway()
        self.stripe = StripeGateway()
        self.eft = EFTProcessor()
        
        # Payment configuration
        self.payment_config = {
            'default_currency': 'ZAR',
            'allowed_currencies': ['ZAR', 'USD'],
            'payment_methods': ['payfast', 'stripe', 'eft'],
            'auto_retry_failed': True,
            'max_retry_attempts': 3
        }
    
    def process_payment(self, client_id: int, amount: Decimal, payment_method: str, 
                      payment_details: Dict) -> Dict:
        """Process payment through selected gateway"""
        self.logger.info(f"Processing {payment_method} payment for client {client_id}")
        
        try:
            # Validate payment details
            if not self._validate_payment_details(payment_method, payment_details):
                return {
                    'success': False,
                    'error': 'Invalid payment details',
                    'payment_id': None
                }
            
            # Process based on payment method
            if payment_method == 'payfast':
                result = self.payfast.create_payment_request(amount, payment_details)
            elif payment_method == 'stripe':
                result = self.stripe.create_payment_intent(amount, payment_details)
            elif payment_method == 'eft':
                result = self.eft.process_eft_payment(amount, payment_details)
            else:
                return {
                    'success': False,
                    'error': 'Unsupported payment method',
                    'payment_id': None
                }
            
            # Record payment attempt
            payment_record = self._record_payment_attempt(
                client_id, amount, payment_method, result
            )
            
            if result.get('success'):
                self._update_client_billing(client_id, amount, payment_method)
                self.logger.info(f"Payment successful: {result.get('payment_id')}")
            else:
                self.logger.warning(f"Payment failed: {result.get('error')}")
            
            return {
                'success': result.get('success', False),
                'payment_id': result.get('payment_id'),
                'gateway_response': result,
                'client_reference': payment_record['id'],
                'next_actions': result.get('next_actions', [])
            }
            
        except Exception as e:
            self.logger.error(f"Payment processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'payment_id': None
            }
    
    def handle_payment_webhook(self, gateway: str, payload: Dict, signature: str) -> bool:
        """Handle payment gateway webhooks"""
        try:
            if gateway == 'payfast':
                return self.payfast.verify_webhook(payload, signature)
            elif gateway == 'stripe':
                return self.stripe.verify_webhook(payload, signature)
            else:
                self.logger.error(f"Unknown webhook gateway: {gateway}")
                return False
                
        except Exception as e:
            self.logger.error(f"Webhook handling error: {e}")
            return False
    
    def _validate_payment_details(self, payment_method: str, details: Dict) -> bool:
        """Validate payment details based on method"""
        validators = {
            'payfast': self._validate_payfast_details,
            'stripe': self._validate_stripe_details,
            'eft': self._validate_eft_details
        }
        
        validator = validators.get(payment_method)
        return validator(details) if validator else False
    
    def _validate_payfast_details(self, details: Dict) -> bool:
        """Validate PayFast payment details"""
        required = ['return_url', 'cancel_url', 'notify_url']
        return all(key in details for key in required)
    
    def _validate_stripe_details(self, details: Dict) -> bool:
        """Validate Stripe payment details"""
        return 'payment_method_id' in details or 'setup_future_usage' in details
    
    def _validate_eft_details(self, details: Dict) -> bool:
        """Validate EFT payment details"""
        required = ['bank_name', 'account_holder', 'reference']
        return all(key in details for key in required)
    
    def _record_payment_attempt(self, client_id: int, amount: Decimal, 
                              method: str, gateway_result: Dict) -> Dict:
        """Record payment attempt in database"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO payment_attempts 
                (client_id, amount, currency, payment_method, gateway, 
                 gateway_reference, status, gateway_response, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                client_id, float(amount), 'ZAR', method, 
                gateway_result.get('gateway', method),
                gateway_result.get('payment_id'),
                gateway_result.get('status', 'pending'),
                json.dumps(gateway_result),
                datetime.now()
            ))
            
            payment_id = cursor.lastrowid
            self.db.commit()
            
            return {
                'id': payment_id,
                'client_id': client_id,
                'amount': amount,
                'method': method,
                'status': gateway_result.get('status', 'pending')
            }
            
        except Exception as e:
            self.logger.error(f"Error recording payment attempt: {e}")
            return {}
    
    def _update_client_billing(self, client_id: int, amount: Decimal, method: str):
        """Update client billing records"""
        try:
            cursor = self.db.cursor()
            
            # Record successful payment
            cursor.execute('''
                INSERT INTO client_payments 
                (client_id, amount, currency, payment_method, payment_date, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (client_id, float(amount), 'ZAR', method, datetime.now().date(), datetime.now()))
            
            # Update client's last payment date
            cursor.execute('''
                UPDATE clients 
                SET last_payment_date = ?, updated_at = ?
                WHERE id = ?
            ''', (datetime.now(), datetime.now(), client_id))
            
            self.db.commit()
            self.logger.info(f"Updated billing for client {client_id}")
            
        except Exception as e:
            self.logger.error(f"Error updating client billing: {e}")
    
    def get_payment_status(self, payment_id: str) -> Dict:
        """Get payment status from gateway"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT gateway, gateway_reference FROM payment_attempts 
                WHERE id = ? OR gateway_reference = ?
            ''', (payment_id, payment_id))
            
            result = cursor.fetchone()
            if not result:
                return {'error': 'Payment not found'}
            
            gateway, gateway_ref = result
            
            if gateway == 'payfast':
                return self.payfast.get_payment_status(gateway_ref)
            elif gateway == 'stripe':
                return self.stripe.get_payment_intent(gateway_ref)
            else:
                return {'error': 'Status check not available for this gateway'}
                
        except Exception as e:
            self.logger.error(f"Payment status check error: {e}")
            return {'error': str(e)}
    
    def generate_payment_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate payment processing report"""
        try:
            cursor = self.db.cursor()
            
            # Payment summary by method
            cursor.execute('''
                SELECT 
                    payment_method,
                    COUNT(*) as attempt_count,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN status = 'completed' THEN amount ELSE 0 END) as total_amount
                FROM payment_attempts 
                WHERE created_at BETWEEN ? AND ?
                GROUP BY payment_method
            ''', (start_date, end_date))
            
            method_summary = {}
            for row in cursor.fetchall():
                method_summary[row[0]] = {
                    'attempts': row[1],
                    'successful': row[2],
                    'success_rate': (row[2] / row[1]) * 100 if row[1] > 0 else 0,
                    'total_amount': row[3]
                }
            
            # Daily payment volume
            cursor.execute('''
                SELECT 
                    DATE(created_at) as payment_date,
                    COUNT(*) as payment_count,
                    SUM(amount) as daily_amount
                FROM payment_attempts 
                WHERE status = 'completed' AND created_at BETWEEN ? AND ?
                GROUP BY DATE(created_at)
                ORDER BY payment_date
            ''', (start_date, end_date))
            
            daily_volume = []
            for row in cursor.fetchall():
                daily_volume.append({
                    'date': row[0],
                    'count': row[1],
                    'amount': row[2]
                })
            
            return {
                'report_period': {
                    'start': start_date,
                    'end': end_date
                },
                'method_summary': method_summary,
                'daily_volume': daily_volume,
                'total_processed': sum(method['total_amount'] for method in method_summary.values())
            }
            
        except Exception as e:
            self.logger.error(f"Payment report error: {e}")
            return {}
