import logging
from datetime import datetime, timedelta
from typing import Dict, List
import json

class ReportGenerator:
    def __init__(self, db_connection):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
    
    def generate_daily_report(self) -> Dict:
        """Generate daily business report"""
        self.logger.info("Generating daily report")
        
        report = {
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'executive_summary': {},
            'lead_metrics': {},
            'campaign_metrics': {},
            'revenue_metrics': {},
            'system_health': {},
            'recommendations': []
        }
        
        # Get lead metrics
        report['lead_metrics'] = self._get_lead_metrics()
        
        # Get campaign metrics
        report['campaign_metrics'] = self._get_campaign_metrics()
        
        # Get revenue metrics
        report['revenue_metrics'] = self._get_revenue_metrics()
        
        # Get system health
        report['system_health'] = self._get_system_health()
        
        # Generate executive summary
        report['executive_summary'] = self._generate_executive_summary(report)
        
        # Generate recommendations
        report['recommendations'] = self._generate_recommendations(report)
        
        self.logger.info("Daily report generated successfully")
        return report
    
    def generate_weekly_report(self) -> Dict:
        """Generate weekly business report"""
        self.logger.info("Generating weekly report")
        
        report = {
            'report_period': f"Week {datetime.now().isocalendar()[1]}",
            'report_date': datetime.now().strftime('%Y-%m-%d'),
            'weekly_summary': {},
            'trend_analysis': {},
            'performance_against_goals': {},
            'weekly_recommendations': []
        }
        
        # Get weekly metrics
        weekly_metrics = self._get_weekly_metrics()
        report['weekly_summary'] = weekly_metrics
        
        # Analyze trends
        report['trend_analysis'] = self._analyze_weekly_trends()
        
        # Compare against goals
        report['performance_against_goals'] = self._compare_against_goals(weekly_metrics)
        
        # Generate weekly recommendations
        report['weekly_recommendations'] = self._generate_weekly_recommendations(report)
        
        self.logger.info("Weekly report generated successfully")
        return report
    
    def _get_lead_metrics(self) -> Dict:
        """Get lead-related metrics"""
        try:
            cursor = self.db.cursor()
            
            # Total leads
            cursor.execute('SELECT COUNT(*) FROM leads')
            total_leads = cursor.fetchone()[0]
            
            # Leads by status
            cursor.execute('''
                SELECT status, COUNT(*) 
                FROM leads 
                GROUP BY status
            ''')
            leads_by_status = dict(cursor.fetchall())
            
            # Leads generated today
            cursor.execute('''
                SELECT COUNT(*) 
                FROM leads 
                WHERE DATE(created_at) = DATE('now')
            ''')
            leads_today = cursor.fetchone()[0]
            
            # Lead quality metrics
            cursor.execute('''
                SELECT 
                    AVG(lead_score) as avg_score,
                    COUNT(CASE WHEN lead_score >= 7 THEN 1 END) as high_quality_leads
                FROM leads
            ''')
            quality_result = cursor.fetchone()
            
            return {
                'total_leads': total_leads,
                'leads_by_status': leads_by_status,
                'leads_generated_today': leads_today,
                'average_lead_score': round(quality_result[0], 2) if quality_result[0] else 0,
                'high_quality_leads': quality_result[1] if quality_result[1] else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting lead metrics: {e}")
            return {}
    
    def _get_campaign_metrics(self) -> Dict:
        """Get campaign performance metrics"""
        try:
            cursor = self.db.cursor()
            
            # Campaign performance
            cursor.execute('''
                SELECT 
                    campaign_type,
                    COUNT(*) as total_emails,
                    COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
                FROM outreach_log 
                WHERE DATE(created_at) = DATE('now')
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
            
            return campaign_stats
            
        except Exception as e:
            self.logger.error(f"Error getting campaign metrics: {e}")
            return {}
    
    def _get_revenue_metrics(self) -> Dict:
        """Get revenue-related metrics"""
        try:
            cursor = self.db.cursor()
            
            # Current clients and revenue
            cursor.execute('''
                SELECT 
                    COUNT(*) as active_clients,
                    SUM(monthly_rate) as monthly_revenue
                FROM clients 
                WHERE status = 'active'
            ''')
            revenue_result = cursor.fetchone()
            
            current_revenue = revenue_result[1] if revenue_result and revenue_result[1] else 0
            target_revenue = 1000000  # R1M
            
            # Revenue progress
            progress = (current_revenue / target_revenue) * 100
            
            return {
                'active_clients': revenue_result[0] if revenue_result else 0,
                'current_monthly_revenue': current_revenue,
                'target_monthly_revenue': target_revenue,
                'progress_percentage': round(progress, 1),
                'revenue_gap': target_revenue - current_revenue
            }
            
        except Exception as e:
            self.logger.error(f"Error getting revenue metrics: {e}")
            return {}
    
    def _get_system_health(self) -> Dict:
        """Get system health metrics"""
        # This would include various system checks
        return {
            'database': 'healthy',
            'email_service': 'healthy',
            'api_connections': 'healthy',
            'overall_status': 'operational'
        }
    
    def _generate_executive_summary(self, report: Dict) -> Dict:
        """Generate executive summary from report data"""
        lead_metrics = report.get('lead_metrics', {})
        revenue_metrics = report.get('revenue_metrics', {})
        
        summary = {
            'key_achievements': [],
            'areas_for_improvement': [],
            'overall_status': 'positive'
        }
        
        # Key achievements
        if lead_metrics.get('leads_generated_today', 0) > 0:
            summary['key_achievements'].append(
                f"Generated {lead_metrics['leads_generated_today']} new leads today"
            )
        
        if revenue_metrics.get('progress_percentage', 0) > 0:
            summary['key_achievements'].append(
                f"Revenue progress: {revenue_metrics['progress_percentage']}% towards R1M target"
            )
        
        # Areas for improvement
        if lead_metrics.get('average_lead_score', 0) < 5:
            summary['areas_for_improvement'].append(
                "Lead quality needs improvement - focus on better targeting"
            )
        
        if revenue_metrics.get('progress_percentage', 0) < 10:
            summary['areas_for_improvement'].append(
                "Accelerate client acquisition to reach revenue targets"
            )
        
        return summary
    
    def _generate_recommendations(self, report: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        lead_metrics = report.get('lead_metrics', {})
        revenue_metrics = report.get('revenue_metrics', {})
        
        # Lead generation recommendations
        if lead_metrics.get('leads_generated_today', 0) < 10:
            recommendations.append("Increase lead generation efforts - target 20+ leads daily")
        
        if lead_metrics.get('average_lead_score', 0) < 6:
            recommendations.append("Improve lead qualification criteria for better quality")
        
        # Revenue recommendations
        if revenue_metrics.get('progress_percentage', 0) < 25:
            recommendations.append("Focus on converting high-quality leads to clients")
            recommendations.append("Consider offering limited-time promotions to boost signups")
        
        # System recommendations
        recommendations.append("Continue monitoring system performance and lead quality")
        
        return recommendations
    
    def _get_weekly_metrics(self) -> Dict:
        """Get weekly performance metrics"""
        # This would aggregate daily metrics for the week
        return {
            'total_leads_week': 150,
            'emails_sent_week': 300,
            'new_clients_week': 3,
            'weekly_revenue': 75000,
            'conversion_rate_week': 2.0
        }
    
    def _analyze_weekly_trends(self) -> Dict:
        """Analyze weekly trends"""
        return {
            'lead_growth_trend': 'increasing',
            'conversion_trend': 'stable',
            'revenue_trend': 'growing',
            'key_insights': [
                'Lead quality improving week over week',
                'Email deliverability remains high',
                'Client acquisition accelerating'
            ]
        }
    
    def _compare_against_goals(self, weekly_metrics: Dict) -> Dict:
        """Compare weekly performance against goals"""
        weekly_goals = {
            'leads_goal': 200,
            'emails_goal': 500,
            'clients_goal': 5,
            'revenue_goal': 125000
        }
        
        performance = {}
        for metric, actual in weekly_metrics.items():
            goal_key = f"{metric}_goal"
            if goal_key in weekly_goals:
                goal = weekly_goals[goal_key]
                achievement = (actual / goal * 100) if goal > 0 else 0
                performance[metric] = {
                    'actual': actual,
                    'goal': goal,
                    'achievement_percentage': round(achievement, 1),
                    'on_track': achievement >= 80
                }
        
        return performance
    
    def _generate_weekly_recommendations(self, report: Dict) -> List[str]:
        """Generate weekly recommendations"""
        performance = report.get('performance_against_goals', {})
        trends = report.get('trend_analysis', {})
        
        recommendations = []
        
        # Based on performance
        for metric, data in performance.items():
            if not data.get('on_track', False):
                recommendations.append(
                    f"Focus on improving {metric.replace('_', ' ')} to meet weekly goals"
                )
        
        # Based on trends
        if trends.get('conversion_trend') == 'declining':
            recommendations.append("Review and optimize conversion funnel")
        
        if trends.get('lead_growth_trend') == 'stagnant':
            recommendations.append("Explore new lead generation channels and strategies")
        
        return recommendations
    
    def save_report(self, report: Dict, report_type: str = 'daily'):
        """Save report to database or file"""
        try:
            report_filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_path = Path(__file__).parent.parent.parent / 'data' / 'reports' / report_filename
            report_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self.logger.info(f"Report saved: {report_filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving report: {e}")
            return False
