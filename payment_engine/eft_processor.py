import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List
import random

class EFTProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.banking_details = self._load_banking_details()
    
    def _load_banking_details(self) -> Dict:
        """Load CostByte banking details for EFT payments"""
        return {
            'bank_name': 'First National Bank',
            'account_name': 'CostByte (Pty) Ltd',
            'account_number': '62736829215',  # Example account number
            'branch_code': '250655',
            'account_type': 'Business Current Account',
            'reference_format': 'CBT{client_id}{invoice_number}'
        }
    
    def process_eft_payment(self, amount: Decimal, payment_data: Dict) -> Dict:
        """Process EFT payment request"""
        try:
            client_id = payment_data.get('client_id')
            invoice_number = payment_data.get('invoice_number', self._generate_invoice_number())
            
            # Generate payment reference
            reference = self._generate_payment_reference(client_id, invoice_number)
            
            # Create EFT payment record
            eft_details = {
                'bank_name': self.banking_details['bank_name'],
                'account_name': self.banking_details['account_name'],
                'account_number': self.banking_details['account_number'],
                'branch_code': self.banking_details['branch_code'],
                'amount': float(amount),
                'reference': reference,
                'due_date': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
                'invoice_number': invoice_number,
                'payment_instructions': self._generate_payment_instructions()
            }
            
            self.logger.info(f"Created EFT payment request: {reference} for amount {amount}")
            
            return {
                'success': True,
                'payment_id': reference,
                'gateway': 'eft',
                'status': 'pending',
                'eft_details': eft_details,
                'next_actions': [
                    'Send banking details to client',
                    'Monitor bank account for payment',
                    'Update payment status when received'
                ]
            }
            
        except Exception as e:
            self.logger.error(f"EFT payment processing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'eft'
            }
    
    def check_eft_payments(self, db_connection) -> List[Dict]:
        """Check for received EFT payments (would integrate with bank API)"""
        try:
            # In production, this would connect to bank API
            # For now, we'll simulate checking for payments
            
            cursor = db_connection.cursor()
            cursor.execute('''
                SELECT pa.id, pa.client_id, pa.amount, pa.gateway_reference
                FROM payment_attempts pa
                WHERE pa.payment_method = 'eft' 
                AND pa.status = 'pending'
                AND pa.created_at >= datetime('now', '-7 days')
            ''')
            
            pending_payments = []
            for row in cursor.fetchall():
                payment_id, client_id, amount, reference = row
                
                # Simulate payment verification (50% chance of payment received)
                payment_received = random.random() > 0.5
                
                if payment_received:
                    pending_payments.append({
                        'payment_id': payment_id,
                        'client_id': client_id,
                        'amount': amount,
                        'reference': reference,
                        'status': 'completed',
                        'verified_at': datetime.now()
                    })
            
            return pending_payments
            
        except Exception as e:
            self.logger.error(f"EFT payment check error: {e}")
            return []
    
    def _generate_invoice_number(self) -> str:
        """Generate unique invoice number"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = random.randint(1000, 9999)
        return f"INV-{timestamp}-{random_suffix}"
    
    def _generate_payment_reference(self, client_id: int, invoice_number: str) -> str:
        """Generate payment reference"""
        client_ref = str(client_id).zfill(6)
        invoice_ref = invoice_number.replace('INV-', '').split('-')[0]
        return f"CBT{client_ref}{invoice_ref}"
    
    def _generate_payment_instructions(self) -> str:
        """Generate EFT payment instructions for clients"""
        return f"""
        EFT PAYMENT INSTRUCTIONS:
        
        1. Bank: {self.banking_details['bank_name']}
        2. Account Name: {self.banking_details['account_name']}
        3. Account Number: {self.banking_details['account_number']}
        4. Branch Code: {self.banking_details['branch_code']}
        5. Reference: [Use the reference provided above]
        6. Amount: [As per your invoice]
        
        Please use the exact reference number provided to ensure 
        your payment is automatically allocated to your account.
        
        Payments typically reflect within 2-3 business days.
        """
    
    def generate_eft_invoice(self, client_data: Dict, amount: Decimal, 
                           payment_reference: str) -> Dict:
        """Generate EFT invoice for client"""
        return {
            'invoice_number': payment_reference,
            'issue_date': datetime.now().strftime('%Y-%m-%d'),
            'due_date': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'client': client_data,
            'amount': float(amount),
            'banking_details': self.banking_details,
            'reference': payment_reference,
            'items': [
                {
                    'description': 'CostByte AI Lead Generation Service',
                    'quantity': 1,
                    'unit_price': float(amount),
                    'total': float(amount)
                }
            ],
            'total': float(amount),
            'tax_amount': 0.00,  # VAT zero-rated for exports
            'grand_total': float(amount)
        }
