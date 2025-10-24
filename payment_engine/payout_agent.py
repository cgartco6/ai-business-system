import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List
import json

class PayoutAgent:
    def __init__(self, db_connection, encryption_engine):
        self.db = db_connection
        self.encryption = encryption_engine
        self.logger = logging.getLogger(__name__)
        
        # Initialize bank clients
        self.fnb_client = FNBClient()
        self.rnb_client = RNBClient()
        
        # Payout configuration
        self.payout_config = {
            'owner_fnb_account': self._load_encrypted_account('owner_fnb'),
            'ai_fund_rnb_account': self._load_encrypted_account('ai_fund_rnb'),
            'reserve_fnb_account': self._load_encrypted_account('reserve_fnb'),
            'payout_schedule': 'daily',  # daily, weekly, monthly
            'minimum_payout': Decimal('1000.00'),  # Minimum amount to process
            'allocation_rules': {
                'owner': Decimal('0.60'),    # 60% to owner
                'ai_fund': Decimal('0.20'),  # 20% to AI fund
                'reserve': Decimal('0.20')   # 20% to reserve
            }
        }
    
    def _load_encrypted_account(self, account_type: str) -> Dict:
        """Load encrypted bank account details"""
        # In production, these would be securely stored and encrypted
        accounts = {
            'owner_fnb': {
                'account_name': 'Owner Personal Account',
                'account_number': 'encrypted_account_001',
                'branch_code': '250655',
                'account_type': 'Current Account'
            },
            'ai_fund_rnb': {
                'account_name': 'CostByte AI Development Fund',
                'account_number': 'encrypted_account_002', 
                'branch_code': '198765',
                'account_type': 'Savings Account'
            },
            'reserve_fnb': {
                'account_name': 'CostByte Business Reserve',
                'account_number': 'encrypted_account_003',
                'branch_code': '250655',
                'account_type': 'Savings Account'
            }
        }
        return accounts.get(account_type, {})
    
    def process_daily_payouts(self) -> Dict:
        """Process daily revenue payouts"""
        try:
            self.logger.info("Starting daily payout processing...")
            
            # Get revenue available for payout
            available_revenue = self._get_available_revenue()
            if available_revenue < self.payout_config['minimum_payout']:
                self.logger.info(f"Insufficient funds for payout: {available_revenue}")
                return {
                    'success': False,
                    'reason': f'Below minimum payout threshold: {self.payout_config["minimum_payout"]}',
                    'available_revenue': float(available_revenue)
                }
            
            # Calculate allocations
            allocations = self._calculate_allocations(available_revenue)
            
            # Execute payouts
            payout_results = self._execute_payouts(allocations)
            
            # Record payout transactions
            self._record_payouts(allocations, payout_results)
            
            self.logger.info(f"Daily payouts completed: {allocations}")
            
            return {
                'success': True,
                'total_payout': float(available_revenue),
                'allocations': allocations,
                'payout_results': payout_results,
                'processed_at': datetime.now()
            }
            
        except Exception as e:
            self.logger.error(f"Daily payout processing error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_available_revenue(self) -> Decimal:
        """Calculate revenue available for payout"""
        try:
            cursor = self.db.cursor()
            
            # Get revenue from last period that hasn't been paid out
            cursor.execute('''
                SELECT COALESCE(SUM(amount), 0) as available_revenue
                FROM client_payments 
                WHERE payment_date >= date('now', '-1 day')
                AND id NOT IN (
                    SELECT payment_id FROM payout_transactions WHERE status = 'completed'
                )
            ''')
            
            result = cursor.fetchone()
            return Decimal(str(result[0])) if result else Decimal('0.00')
            
        except Exception as e:
            self.logger.error(f"Revenue calculation error: {e}")
            return Decimal('0.00')
    
    def _calculate_allocations(self, total_revenue: Decimal) -> Dict:
        """Calculate payout allocations according to rules"""
        rules = self.payout_config['allocation_rules']
        
        allocations = {}
        for category, percentage in rules.items():
            amount = total_revenue * percentage
            allocations[category] = {
                'amount': amount,
                'percentage': float(percentage) * 100,
                'account': self._get_destination_account(category)
            }
        
        return allocations
    
    def _get_destination_account(self, category: str) -> Dict:
        """Get destination account for payout category"""
        account_map = {
            'owner': self.payout_config['owner_fnb_account'],
            'ai_fund': self.payout_config['ai_fund_rnb_account'], 
            'reserve': self.payout_config['reserve_fnb_account']
        }
        return account_map.get(category, {})
    
    def _execute_payouts(self, allocations: Dict) -> Dict:
        """Execute payouts to respective bank accounts"""
        results = {}
        
        for category, allocation in allocations.items():
            amount = allocation['amount']
            account = allocation['account']
            
            try:
                if 'fnb' in account.get('account_number', ''):
                    # Transfer to FNB account
                    result = self.fnb_client.transfer_funds(
                        amount=float(amount),
                        to_account=account['account_number'],
                        to_branch=account['branch_code'],
                        description=f"CostByte {category.title()} Payout"
                    )
                elif 'rnb' in account.get('account_number', ''):
                    # Transfer to RNB account  
                    result = self.rnb_client.transfer_funds(
                        amount=float(amount),
                        to_account=account['account_number'],
                        description=f"CostByte {category.title()} Fund Allocation"
                    )
                else:
                    result = {'success': False, 'error': 'Unknown bank'}
                
                results[category] = result
                
            except Exception as e:
                self.logger.error(f"Payout execution error for {category}: {e}")
                results[category] = {
                    'success': False,
                    'error': str(e)
                }
        
        return results
    
    def _record_payouts(self, allocations: Dict, payout_results: Dict):
        """Record payout transactions in database"""
        try:
            cursor = self.db.cursor()
            
            for category, allocation in allocations.items():
                result = payout_results.get(category, {})
                
                cursor.execute('''
                    INSERT INTO payout_transactions 
                    (category, amount, percentage, destination_account, 
                     status, reference, payout_date, recorded_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    category,
                    float(allocation['amount']),
                    allocation['percentage'],
                    allocation['account'].get('account_name', ''),
                    'completed' if result.get('success') else 'failed',
                    result.get('reference', ''),
                    datetime.now().date(),
                    datetime.now()
                ))
            
            self.db.commit()
            self.logger.info("Payout transactions recorded successfully")
            
        except Exception as e:
            self.logger.error(f"Payout recording error: {e}")
    
    def get_payout_history(self, days: int = 30) -> List[Dict]:
        """Get payout history for specified period"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute('''
                SELECT 
                    category,
                    SUM(amount) as total_amount,
                    COUNT(*) as transaction_count,
                    MIN(payout_date) as first_payout,
                    MAX(payout_date) as last_payout
                FROM payout_transactions 
                WHERE payout_date >= date('now', ?)
                GROUP BY category
            ''', (f'-{days} days',))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'category': row[0],
                    'total_amount': row[1],
                    'transaction_count': row[2],
                    'first_payout': row[3],
                    'last_payout': row[4]
                })
            
            return history
            
        except Exception as e:
            self.logger.error(f"Payout history error: {e}")
            return []
    
    def generate_payout_report(self, start_date: datetime, end_date: datetime) -> Dict:
        """Generate comprehensive payout report"""
        try:
            cursor = self.db.cursor()
            
            # Total payouts by category
            cursor.execute('''
                SELECT 
                    category,
                    SUM(amount) as total_paid,
                    COUNT(*) as payout_count
                FROM payout_transactions 
                WHERE payout_date BETWEEN ? AND ?
                GROUP BY category
            ''', (start_date.date(), end_date.date()))
            
            category_summary = {}
            for row in cursor.fetchall():
                category_summary[row[0]] = {
                    'total_paid': row[1],
                    'payout_count': row[2]
                }
            
            # Daily payout volume
            cursor.execute('''
                SELECT 
                    payout_date,
                    SUM(amount) as daily_total,
                    COUNT(*) as daily_count
                FROM payout_transactions 
                WHERE payout_date BETWEEN ? AND ?
                GROUP BY payout_date
                ORDER BY payout_date
            ''', (start_date.date(), end_date.date()))
            
            daily_volume = []
            for row in cursor.fetchall():
                daily_volume.append({
                    'date': row[0],
                    'total_amount': row[1],
                    'transaction_count': row[2]
                })
            
            return {
                'report_period': {
                    'start': start_date,
                    'end': end_date
                },
                'category_summary': category_summary,
                'daily_volume': daily_volume,
                'total_payouts': sum(cat['total_paid'] for cat in category_summary.values())
            }
            
        except Exception as e:
            self.logger.error(f"Payout report error: {e}")
            return {}
