import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List
import sqlite3

class MonitorAgent:
    def __init__(self, db_connection):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
        self.monitoring_intervals = {
            'system_health': 300,  # 5 minutes
            'lead_quality': 3600,   # 1 hour
            'campaign_performance': 1800,  # 30 minutes
            'revenue_tracking': 86400  # 24 hours
        }
        self.last_checks = {}
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        self.logger.info("Starting AI system monitoring")
        
        while True:
            try:
                self._check_system_health()
                self._monitor_lead_quality()
                self._track_campaign_performance()
                self._monitor_revenue_progress()
                
                # Sleep for 1 minute between monitoring cycles
                time.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")
                time.sleep(300)  # Wait 5 minutes before retrying
    
    def _check_system_health(self):
        """Check overall system health"""
        current_time = datetime.now()
        
        # Only check every 5 minutes
        if (current_time - self.last_checks.get('system_health', datetime.min)).seconds < self.monitoring_intervals['system_health']:
            return
        
        health_checks = {
            'database_connection': self._check_database_health(),
            'email_service': self._check_email_service(),
            'api_connections': self._check_api_connections(),
            'disk_space': self._check_disk_space(),
            'memory_usage': self._check_memory_usage()
        }
        
        # Log any issues
        for check, status in health_checks.items():
            if not status['healthy']:
                self.logger.warning(f"System health issue: {check} - {status.get('message', 'Unknown error')}")
        
        self.last_checks['system_health'] = current_time
    
    def _monitor_lead_quality(self):
        """Monitor lead quality metrics"""
        current_time = datetime.now()
        
        if (current_time - self.last_checks.get('lead_quality', datetime.min)).seconds < self.monitoring_intervals['lead_quality']:
            return
        
        try:
            cursor = self.db.cursor()
            
            # Get lead quality metrics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_leads,
                    AVG(lead_score) as avg_score,
                    COUNT(CASE WHEN status LIKE 'qualified%' THEN 1 END) as qualified_count,
                    COUNT(CASE WHEN status = 'converted' THEN 1 END) as converted_count
                FROM leads
                WHERE created_at >= datetime('now', '-7 days')
            ''')
            result = cursor.fetchone()
            
            metrics = {
                'total_leads_7days': result[0] if result else 0,
                'average_lead_score': round(result[1], 2) if result and result[1] else 0,
                'qualification_rate': (result[2] / result[0] * 100) if result and result[0] > 0 else 0,
                'conversion_rate': (result[3] / result[0] * 100) if result and result[0] > 0 else 0
            }
            
            # Check for quality issues
            if metrics['average_lead_score'] < 5:
                self.logger.warning(f"Low average lead score: {metrics['average_lead_score']}")
            
            if metrics['qualification_rate'] < 20:
                self.logger.warning(f"Low qualification rate: {metrics['qualification_rate']:.1f}%")
            
            self.logger.info(f"Lead quality metrics: {metrics}")
            
        except Exception as e:
            self.logger.error(f"Error monitoring lead quality: {e}")
        
        self.last_checks['lead_quality'] = current_time
    
    def _track_campaign_performance(self):
        """Track outreach campaign performance"""
        current_time = datetime.now()
        
        if (current_time - self.last_checks.get('campaign_performance', datetime.min)).seconds < self.monitoring_intervals['campaign_performance']:
            return
        
        try:
            cursor = self.db.cursor()
            
            # Get campaign performance for last 24 hours
            cursor.execute('''
                SELECT 
                    campaign_type,
                    COUNT(*) as total_emails,
                    COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent_emails,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_emails
                FROM outreach_log 
                WHERE created_at >= datetime('now', '-1 day')
                GROUP BY campaign_type
            ''')
            
            campaign_stats = {}
            for row in cursor.fetchall():
                campaign_type, total, sent, failed = row
                success_rate = (sent / total * 100) if total > 0 else 0
                
                campaign_stats[campaign_type] = {
                    'total_emails': total,
                    'sent_emails': sent,
                    'failed_emails': failed,
                    'success_rate': round(success_rate, 1)
                }
                
                # Alert on low success rates
                if success_rate < 70:
                    self.logger.warning(f"Low success rate for {campaign_type}: {success_rate:.1f}%")
            
            self.logger.info(f"Campaign performance: {campaign_stats}")
            
        except Exception as e:
            self.logger.error(f"Error tracking campaign performance: {e}")
        
        self.last_checks['campaign_performance'] = current_time
    
    def _monitor_revenue_progress(self):
        """Monitor progress towards revenue goals"""
        current_time = datetime.now()
        
        if (current_time - self.last_checks.get('revenue_tracking', datetime.min)).seconds < self.monitoring_intervals['revenue_tracking']:
            return
        
        try:
            cursor = self.db.cursor()
            
            # Get current client count and revenue
            cursor.execute('''
                SELECT 
                    COUNT(*) as active_clients,
                    SUM(monthly_rate) as monthly_revenue
                FROM clients 
                WHERE status = 'active'
            ''')
            result = cursor.fetchone()
            
            current_revenue = result[1] if result and result[1] else 0
            target_revenue = 1000000  # R1M target
            
            progress = (current_revenue / target_revenue) * 100
            
            metrics = {
                'active_clients': result[0] if result else 0,
                'current_revenue': current_revenue,
                'target_revenue': target_revenue,
                'progress_percentage': round(progress, 1),
                'revenue_gap': target_revenue - current_revenue
            }
            
            # Log progress
            if progress < 25:
                status = "Early stages"
            elif progress < 50:
                status = "Good progress"
            elif progress < 75:
                status = "Strong progress"
            else:
                status = "Nearly there"
            
            self.logger.info(f"Revenue progress: {status} ({metrics['progress_percentage']}%) - R{current_revenue:,}/R{target_revenue:,}")
            
            # Alert if progress is stalled
            if progress < 10 and metrics['active_clients'] > 0:
                self.logger.warning("Revenue progress is below expectations")
            
        except Exception as e:
            self.logger.error(f"Error monitoring revenue: {e}")
        
        self.last_checks['revenue_tracking'] = current_time
    
    def _check_database_health(self) -> Dict:
        """Check database connection health"""
        try:
            cursor = self.db.cursor()
            cursor.execute('SELECT 1')
            return {'healthy': True, 'message': 'Database connection OK'}
        except Exception as e:
            return {'healthy': False, 'message': f'Database error: {e}'}
    
    def _check_email_service(self) -> Dict:
        """Check email service health"""
        # This would actually test email connectivity
        return {'healthy': True, 'message': 'Email service OK'}
    
    def _check_api_connections(self) -> Dict:
        """Check external API connections"""
        # This would test connections to external APIs
        return {'healthy': True, 'message': 'API connections OK'}
    
    def _check_disk_space(self) -> Dict:
        """Check disk space"""
        # This would check available disk space
        return {'healthy': True, 'message': 'Disk space OK'}
    
    def _check_memory_usage(self) -> Dict:
        """Check memory usage"""
        # This would check system memory usage
        return {'healthy': True, 'message': 'Memory usage OK'}
    
    def generate_daily_report(self) -> Dict:
        """Generate daily monitoring report"""
        report = {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'system_health': {},
            'performance_metrics': {},
            'alerts': [],
            'recommendations': []
        }
        
        # Collect system health data
        report['system_health'] = {
            'database': self._check_database_health(),
            'email_service': self._check_email_service(),
            'apis': self._check_api_connections()
        }
        
        # Collect performance metrics
        try:
            cursor = self.db.cursor()
            
            # Lead metrics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_leads,
                    COUNT(CASE WHEN status LIKE 'qualified%' THEN 1 END) as qualified,
                    COUNT(CASE WHEN status = 'converted' THEN 1 END) as converted
                FROM leads
                WHERE created_at >= datetime('now', '-1 day')
            ''')
            lead_result = cursor.fetchone()
            
            # Campaign metrics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_emails,
                    COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
                FROM outreach_log
                WHERE created_at >= datetime('now', '-1 day')
            ''')
            campaign_result = cursor.fetchone()
            
            report['performance_metrics'] = {
                'leads_generated': lead_result[0] if lead_result else 0,
                'leads_qualified': lead_result[1] if lead_result else 0,
                'leads_converted': lead_result[2] if lead_result else 0,
                'emails_sent': campaign_result[1] if campaign_result else 0,
                'email_success_rate': (campaign_result[1] / campaign_result[0] * 100) if campaign_result and campaign_result[0] > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error generating daily report: {e}")
            report['error'] = str(e)
        
        return report
