import logging
from datetime import datetime
from decimal import Decimal

class AutoFundingEngine:
    def __init__(self, db_connection):
        self.db = db_connection
        self.funding_rules = {
            'platform_maintenance': Decimal('0.10'),  # 10%
            'owner_compensation': Decimal('0.30'),    # 30%
            'reinvestment': Decimal('0.40'),          # 40%
            'tax_reserve': Decimal('0.20')            # 20%
        }
    
    def process_revenue_allocation(self, revenue_amount):
        """Automatically allocate revenue according to funding rules"""
        allocations = {}
        
        for category, percentage in self.funding_rules.items():
            allocation = revenue_amount * percentage
            allocations[category] = float(allocation)
            
            # Record the allocation
            self._record_allocation(category, allocation, revenue_amount)
        
        logging.info(f"Revenue allocation completed: {allocations}")
        return allocations
    
    def _record_allocation(self, category, amount, total_revenue):
        """Record revenue allocation in database"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO revenue_allocations 
                (category, amount, total_revenue, allocation_date, recorded_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (category, float(amount), float(total_revenue), datetime.now().date(), datetime.now()))
            
            self.db.commit()
            
        except Exception as e:
            logging.error(f"Error recording revenue allocation: {e}")
    
    def execute_funding_transfers(self):
        """Execute actual funding transfers to different accounts"""
        try:
            cursor = self.db.cursor()
            
            # Get unprocessed allocations
            cursor.execute('''
                SELECT category, SUM(amount) as total_amount
                FROM revenue_allocations 
                WHERE transfer_executed = 0
                GROUP BY category
            ''')
            
            pending_transfers = cursor.fetchall()
            
            transfers_executed = []
            
            for category, amount in pending_transfers:
                # In a real system, this would initiate actual bank transfers
                # For now, we'll just mark them as executed
                
                success = self._execute_bank_transfer(category, amount)
                
                if success:
                    # Mark as executed
                    cursor.execute('''
                        UPDATE revenue_allocations 
                        SET transfer_executed = 1, transfer_date = ?
                        WHERE category = ? AND transfer_executed = 0
                    ''', (datetime.now(), category))
                    
                    transfers_executed.append({
                        'category': category,
                        'amount': amount,
                        'timestamp': datetime.now()
                    })
                    
                    logging.info(f"Executed funding transfer: {category} - {amount} ZAR")
            
            self.db.commit()
            return transfers_executed
            
        except Exception as e:
            logging.error(f"Error executing funding transfers: {e}")
            return []
    
    def _execute_bank_transfer(self, category, amount):
        """Execute actual bank transfer (placeholder for banking API integration)"""
        # This would integrate with actual banking APIs
        # For now, we'll simulate successful transfers
        
        bank_accounts = {
            'platform_maintenance': 'Platform Operations Account',
            'owner_compensation': 'Owner Personal Account', 
            'reinvestment': 'Business Growth Account',
            'tax_reserve': 'Tax Reserve Account'
        }
        
        target_account = bank_accounts.get(category)
        if target_account:
            logging.info(f"Transferring {amount} ZAR to {target_account}")
            return True
        else:
            logging.error(f"Unknown category for bank transfer: {category}")
            return False
    
    def get_funding_report(self):
        """Generate funding allocation report"""
        try:
            cursor = self.db.cursor()
            
            # Current month allocations
            cursor.execute('''
                SELECT 
                    category,
                    SUM(amount) as allocated_amount,
                    COUNT(*) as allocation_count
                FROM revenue_allocations 
                WHERE strftime('%Y-%m', allocation_date) = strftime('%Y-%m', 'now')
                GROUP BY category
            ''')
            
            current_allocations = {}
            for row in cursor.fetchall():
                current_allocations[row[0]] = {
                    'allocated_amount': row[1],
                    'allocation_count': row[2]
                }
            
            # Transfer status
            cursor.execute('''
                SELECT 
                    category,
                    SUM(CASE WHEN transfer_executed = 1 THEN amount ELSE 0 END) as transferred_amount,
                    SUM(CASE WHEN transfer_executed = 0 THEN amount ELSE 0 END) as pending_amount
                FROM revenue_allocations 
                WHERE strftime('%Y-%m', allocation_date) = strftime('%Y-%m', 'now')
                GROUP BY category
            ''')
            
            transfer_status = {}
            for row in cursor.fetchall():
                transfer_status[row[0]] = {
                    'transferred_amount': row[1],
                    'pending_amount': row[2]
                }
            
            return {
                'current_allocations': current_allocations,
                'transfer_status': transfer_status,
                'funding_rules': self.funding_rules,
                'report_date': datetime.now().strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            logging.error(f"Error generating funding report: {e}")
            return {}
