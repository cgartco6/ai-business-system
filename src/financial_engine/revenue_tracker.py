import logging
from datetime import datetime, timedelta
from decimal import Decimal
import json

class RevenueTracker:
    def __init__(self, db_connection):
        self.db = db_connection
        self.currency = 'ZAR'
        
    def record_client_payment(self, client_id, amount, payment_date=None, service_tier='professional'):
        """Record client payment and update revenue tracking"""
        if payment_date is None:
            payment_date = datetime.now()
        
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO client_payments 
                (client_id, amount, currency, payment_date, service_tier, recorded_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (client_id, float(amount), self.currency, payment_date, service_tier, datetime.now()))
            
            self.db.commit()
            
            # Update client revenue summary
            self._update_client_revenue_summary(client_id)
            
            # Update overall revenue tracking
            self._update_revenue_metrics()
            
            logging.info(f"Recorded payment: {amount} {self.currency} from client {client_id}")
            return True
            
        except Exception as e:
            logging.error(f"Error recording payment: {e}")
            return False
    
    def _update_client_revenue_summary(self, client_id):
        """Update client revenue summary"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT 
                    SUM(amount) as total_revenue,
                    COUNT(*) as payment_count,
                    MIN(payment_date) as first_payment,
                    MAX(payment_date) as last_payment
                FROM client_payments 
                WHERE client_id = ?
            ''', (client_id,))
            
            result = cursor.fetchone()
            
            cursor.execute('''
                INSERT OR REPLACE INTO client_revenue_summary 
                (client_id, total_revenue, payment_count, first_payment, last_payment, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (client_id, result[0] or 0, result[1] or 0, result[2], result[3], datetime.now()))
            
            self.db.commit()
            
        except Exception as e:
            logging.error(f"Error updating client revenue summary: {e}")
    
    def _update_revenue_metrics(self):
        """Update overall revenue metrics"""
        try:
            cursor = self.db.cursor()
            
            # Monthly revenue
            cursor.execute('''
                SELECT 
                    strftime('%Y-%m', payment_date) as month,
                    SUM(amount) as monthly_revenue,
                    COUNT(DISTINCT client_id) as active_clients
                FROM client_payments 
                WHERE payment_date >= date('now', '-12 months')
                GROUP BY strftime('%Y-%m', payment_date)
                ORDER BY month DESC
            ''')
            
            monthly_results = cursor.fetchall()
            
            # Update monthly metrics
            for month, revenue, clients in monthly_results:
                cursor.execute('''
                    INSERT OR REPLACE INTO monthly_revenue 
                    (month, revenue, active_clients, updated_at)
                    VALUES (?, ?, ?, ?)
                ''', (month, revenue, clients, datetime.now()))
            
            # Current month projections
            current_month = datetime.now().strftime('%Y-%m')
            cursor.execute('''
                SELECT SUM(amount) FROM client_payments 
                WHERE strftime('%Y-%m', payment_date) = ?
            ''', (current_month,))
            
            current_revenue = cursor.fetchone()[0] or 0
            
            # Projected monthly revenue (based on current daily average)
            day_of_month = datetime.now().day
            if day_of_month > 0:
                projected_revenue = (current_revenue / day_of_month) * 30
            else:
                projected_revenue = current_revenue
            
            cursor.execute('''
                INSERT OR REPLACE INTO revenue_projections 
                (projection_date, current_revenue, projected_monthly, updated_at)
                VALUES (?, ?, ?, ?)
            ''', (datetime.now().date(), current_revenue, projected_revenue, datetime.now()))
            
            self.db.commit()
            
        except Exception as e:
            logging.error(f"Error updating revenue metrics: {e}")
    
    def get_revenue_dashboard_data(self):
        """Get data for revenue dashboard"""
        try:
            cursor = self.db.cursor()
            
            # Current month revenue
            cursor.execute('''
                SELECT SUM(amount) FROM client_payments 
                WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')
            ''')
            current_month_revenue = cursor.fetchone()[0] or 0
            
            # Previous month revenue
            cursor.execute('''
                SELECT SUM(amount) FROM client_payments 
                WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now', '-1 month')
            ''')
            previous_month_revenue = cursor.fetchone()[0] or 0
            
            # Active clients
            cursor.execute('''
                SELECT COUNT(DISTINCT client_id) FROM client_payments 
                WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')
            ''')
            active_clients = cursor.fetchone()[0] or 0
            
            # Revenue growth
            if previous_month_revenue > 0:
                growth_percentage = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
            else:
                growth_percentage = 100 if current_month_revenue > 0 else 0
            
            # Monthly trend (last 6 months)
            cursor.execute('''
                SELECT 
                    strftime('%Y-%m', payment_date) as month,
                    SUM(amount) as revenue
                FROM client_payments 
                WHERE payment_date >= date('now', '-6 months')
                GROUP BY strftime('%Y-%m', payment_date)
                ORDER BY month
            ''')
            monthly_trend = [{'month': row[0], 'revenue': row[1]} for row in cursor.fetchall()]
            
            # Client tier distribution
            cursor.execute('''
                SELECT service_tier, COUNT(*) as client_count
                FROM client_payments 
                WHERE strftime('%Y-%m', payment_date) = strftime('%Y-%m', 'now')
                GROUP BY service_tier
            ''')
            tier_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            return {
                'current_month_revenue': current_month_revenue,
                'previous_month_revenue': previous_month_revenue,
                'growth_percentage': round(growth_percentage, 1),
                'active_clients': active_clients,
                'monthly_trend': monthly_trend,
                'tier_distribution': tier_distribution,
                'target_revenue': 1000000,
                'progress_percentage': (current_month_revenue / 1000000) * 100
            }
            
        except Exception as e:
            logging.error(f"Error getting revenue dashboard data: {e}")
            return {}
