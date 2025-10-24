import logging
import stripe
from decimal import Decimal
from typing import Dict, Optional

class StripeGateway:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.config = self._load_config()
        self.stripe = self._initialize_stripe()
    
    def _load_config(self) -> Dict:
        """Load Stripe configuration"""
        return {
            'secret_key': 'sk_test_...',  # Your Stripe secret key
            'public_key': 'pk_test_...',  # Your Stripe public key
            'webhook_secret': 'whsec_...',  # Your webhook secret
            'default_currency': 'zar'
        }
    
    def _initialize_stripe(self) -> stripe:
        """Initialize Stripe SDK"""
        stripe.api_key = self.config['secret_key']
        return stripe
    
    def create_payment_intent(self, amount: Decimal, payment_data: Dict) -> Dict:
        """Create Stripe Payment Intent"""
        try:
            # Convert amount to cents (Stripe requires integer amounts)
            amount_cents = int(amount * 100)
            
            intent_data = {
                'amount': amount_cents,
                'currency': self.config['default_currency'],
                'payment_method_types': ['card'],
                'metadata': {
                    'client_id': payment_data.get('client_id'),
                    'service_tier': payment_data.get('service_tier', 'professional'),
                    'payment_reference': payment_data.get('payment_reference', '')
                }
            }
            
            # Add customer if available
            customer_id = payment_data.get('stripe_customer_id')
            if customer_id:
                intent_data['customer'] = customer_id
            else:
                # Create new customer
                customer = self.stripe.Customer.create(
                    email=payment_data.get('email'),
                    name=payment_data.get('customer_name'),
                    metadata={'client_id': payment_data.get('client_id')}
                )
                intent_data['customer'] = customer.id
            
            # Create payment intent
            intent = self.stripe.PaymentIntent.create(**intent_data)
            
            self.logger.info(f"Created Stripe payment intent: {intent.id}")
            
            return {
                'success': True,
                'payment_id': intent.id,
                'client_secret': intent.client_secret,
                'gateway': 'stripe',
                'status': intent.status,
                'amount_cents': amount_cents,
                'currency': intent.currency
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe payment intent error: {e}")
            return {
                'success': False,
                'error': str(e),
                'gateway': 'stripe'
            }
    
    def verify_webhook(self, payload: bytes, signature: str) -> bool:
        """Verify Stripe webhook signature"""
        try:
            event = self.stripe.Webhook.construct_event(
                payload, signature, self.config['webhook_secret']
            )
            
            # Handle the event
            if event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                self.logger.info(f"Stripe payment succeeded: {payment_intent['id']}")
                return True
            else:
                self.logger.info(f"Unhandled Stripe event type: {event['type']}")
                return False
                
        except ValueError as e:
            self.logger.error(f"Stripe webhook invalid payload: {e}")
            return False
        except stripe.error.SignatureVerificationError as e:
            self.logger.error(f"Stripe webhook signature verification failed: {e}")
            return False
    
    def get_payment_intent(self, payment_intent_id: str) -> Dict:
        """Retrieve Stripe Payment Intent"""
        try:
            intent = self.stripe.PaymentIntent.retrieve(payment_intent_id)
            
            return {
                'success': True,
                'payment_id': intent.id,
                'status': intent.status,
                'amount': intent.amount / 100,  # Convert back to dollars/rand
                'currency': intent.currency,
                'client_secret': intent.client_secret,
                'gateway': 'stripe'
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe payment intent retrieval error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_customer(self, client_data: Dict) -> Dict:
        """Create Stripe customer for recurring payments"""
        try:
            customer = self.stripe.Customer.create(
                email=client_data['email'],
                name=client_data.get('name', ''),
                phone=client_data.get('phone', ''),
                metadata={'client_id': client_data['client_id']}
            )
            
            return {
                'success': True,
                'customer_id': customer.id,
                'gateway': 'stripe'
            }
            
        except stripe.error.StripeError as e:
            self.logger.error(f"Stripe customer creation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
