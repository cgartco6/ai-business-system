import smtplib
import time
from datetime import datetime
import logging
from typing import Dict, List
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

class OutreachAgent:
    def __init__(self, email_manager, db_connection):
        self.email_manager = email_manager
        self.db = db_connection
        self.sent_emails = 0
        self.responses = 0
        self.logger = logging.getLogger(__name__)
        self.campaigns = {}
    
    def execute_outreach_campaign(self, leads: List[Dict], campaign_type: str = 'cold_email') -> List[Dict]:
        """Execute outreach campaign to qualified leads"""
        self.logger.info(f"Starting {campaign_type} campaign for {len(leads)} leads")
        
        results = []
        campaign_id = f"campaign_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.campaigns[campaign_id] = {
            'type': campaign_type,
            'start_time': datetime.now(),
            'target_leads': len(leads),
            'sent_emails': 0,
            'failed_emails': 0
        }
        
        for i, lead in enumerate(leads):
            if lead['priority'] in ['high', 'medium']:
                try:
                    result = self._send_personalized_email(lead, campaign_type, campaign_id)
                    results.append(result)
                    self.sent_emails += 1
                    self.campaigns[campaign_id]['sent_emails'] += 1
                    
                    # Rate limiting to avoid being flagged as spam
                    if (i + 1) % 10 == 0:  # Every 10 emails
                        time.sleep(30)  # 30 second break
                    else:
                        time.sleep(2)   # 2 seconds between emails
                    
                except Exception as e:
                    self.logger.error(f"Failed to send email to {lead['contact_email']}: {e}")
                    self.campaigns[campaign_id]['failed_emails'] += 1
                    results.append({
                        'lead_id': lead.get('id'),
                        'status': 'failed',
                        'error': str(e),
                        'campaign_id': campaign_id
                    })
        
        self.campaigns[campaign_id]['end_time'] = datetime.now()
        self.campaigns[campaign_id]['completion_rate'] = (
            self.campaigns[campaign_id]['sent_emails'] / self.campaigns[campaign_id]['target_leads'] * 100
        )
        
        self.logger.info(f"Campaign {campaign_id} completed: {self.campaigns[campaign_id]['sent_emails']} emails sent")
        return results
    
    def _send_personalized_email(self, lead: Dict, campaign_type: str, campaign_id: str) -> Dict:
        """Send personalized email to lead"""
        from src.synthetic_intelligence.content_generator import ContentGenerator
        content_gen = ContentGenerator()
        
        # Generate personalized content
        subject = content_gen.generate_email_subject({
            'company_name': lead['company_name']
        })
        
        body = content_gen.generate_email_body(lead, campaign_type)
        
        try:
            success = self.email_manager.send_email(
                to_email=lead['contact_email'],
                subject=subject,
                body=body
            )
            
            if success:
                # Log the successful outreach
                self._log_outreach(lead, 'sent', campaign_id, campaign_type)
                
                # Update lead status
                self._update_lead_status(lead['id'], 'contacted')
                
                return {
                    'lead_id': lead.get('id'),
                    'status': 'sent',
                    'sent_at': datetime.now(),
                    'email_subject': subject,
                    'campaign_id': campaign_id
                }
            else:
                raise Exception("Email manager returned failure")
                
        except Exception as e:
            self._log_outreach(lead, 'failed', campaign_id, campaign_type, str(e))
            raise e
    
    def create_follow_up_sequence(self, lead: Dict, initial_contact_date: datetime) -> List[Dict]:
        """Create follow-up sequence for a lead"""
        follow_ups = []
        
        # Follow-up 1: 3 days after initial contact
        follow_ups.append({
            'days_after_initial': 3,
            'type': 'follow_up_1',
            'subject': f"Following up: Growth opportunities for {lead['company_name']}",
            'template': 'follow_up_1'
        })
        
        # Follow-up 2: 7 days after initial contact  
        follow_ups.append({
            'days_after_initial': 7,
            'type': 'follow_up_2',
            'subject': f"Free lead generation assessment for {lead['company_name']}",
            'template': 'follow_up_2'
        })
        
        # Follow-up 3: 14 days after initial contact
        follow_ups.append({
            'days_after_initial': 14,
            'type': 'final_follow_up',
            'subject': f"Final follow-up: AI lead generation for {lead['company_name']}",
            'template': 'final_follow_up'
        })
        
        return follow_ups
    
    def schedule_follow_up(self, lead: Dict, follow_up: Dict):
        """Schedule a follow-up email"""
        scheduled_date = datetime.now()  # This would be calculated based on days_after_initial
        
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO follow_up_schedule 
                (lead_id, follow_up_type, scheduled_date, subject, template, status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                lead['id'], follow_up['type'], scheduled_date, 
                follow_up['subject'], follow_up['template'], 'scheduled'
            ))
            self.db.commit()
            self.logger.info(f"Scheduled follow-up for lead {lead['id']}")
        except Exception as e:
            self.logger.error(f"Error scheduling follow-up: {e}")
    
    def _log_outreach(self, lead: Dict, status: str, campaign_id: str, campaign_type: str, error: str = None):
        """Log outreach activity to database"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO outreach_log 
                (lead_id, campaign_id, campaign_type, status, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (lead.get('id'), campaign_id, campaign_type, status, error, datetime.now()))
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Error logging outreach: {e}")
    
    def _update_lead_status(self, lead_id: str, new_status: str):
        """Update lead status in database"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                UPDATE leads SET status = ?, last_contacted = ? WHERE id = ?
            ''', (new_status, datetime.now(), lead_id))
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Error updating lead status: {e}")
    
    def get_campaign_stats(self, campaign_id: str = None) -> Dict:
        """Get campaign statistics"""
        if campaign_id:
            return self.campaigns.get(campaign_id, {})
        else:
            # Overall stats
            total_campaigns = len(self.campaigns)
            total_sent = sum(camp['sent_emails'] for camp in self.campaigns.values())
            total_failed = sum(camp['failed_emails'] for camp in self.campaigns.values())
            
            return {
                'total_campaigns': total_campaigns,
                'total_emails_sent': total_sent,
                'total_emails_failed': total_failed,
                'success_rate': (total_sent / (total_sent + total_failed)) * 100 if (total_sent + total_failed) > 0 else 0,
                'active_campaigns': len([c for c in self.campaigns.values() if 'end_time' not in c])
            }
