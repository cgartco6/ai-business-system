import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import time
from datetime import datetime
import logging

class OutreachAgent:
    def __init__(self, email_manager, db_connection):
        self.email_manager = email_manager
        self.db = db_connection
        self.sent_emails = 0
        self.responses = 0
        self.logger = logging.getLogger(__name__)
    
    def execute_outreach_campaign(self, leads, campaign_type='cold_email'):
        """Execute outreach campaign to qualified leads"""
        results = []
        
        for lead in leads:
            if lead['priority'] in ['high', 'medium']:
                try:
                    result = self._send_personalized_email(lead, campaign_type)
                    results.append(result)
                    self.sent_emails += 1
                    
                    # Rate limiting to avoid being flagged as spam
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Failed to send email to {lead['contact_email']}: {e}")
                    results.append({
                        'lead_id': lead.get('id'),
                        'status': 'failed',
                        'error': str(e)
                    })
        
        return results
    
    def _send_personalized_email(self, lead, campaign_type):
        """Send personalized email to lead"""
        email_content = self._generate_email_content(lead, campaign_type)
        
        try:
            self.email_manager.send_email(
                to_email=lead['contact_email'],
                subject=email_content['subject'],
                body=email_content['body']
            )
            
            # Log the outreach
            self._log_outreach(lead, 'sent')
            
            return {
                'lead_id': lead.get('id'),
                'status': 'sent',
                'sent_at': datetime.now(),
                'email_subject': email_content['subject']
            }
            
        except Exception as e:
            self._log_outreach(lead, 'failed', str(e))
            raise e
    
    def _generate_email_content(self, lead, campaign_type):
        """Generate personalized email content"""
        if campaign_type == 'cold_email':
            subject = f"Growth opportunity for {lead['company_name']}"
            body = f"""
            Hi Team at {lead['company_name']},
            
            I noticed your company's presence in the {lead['industry']} industry and was impressed by your work.
            
            We specialize in helping businesses like yours generate 20-30 qualified leads per week using AI-powered systems.
            
            Many of our clients in South Africa are achieving remarkable results, with some seeing 3x increases in qualified leads within the first month.
            
            Would you be open to a quick 15-minute call to explore if similar results would be valuable for {lead['company_name']}?
            
            Best regards,
            AI Growth Team
            """
        
        elif campaign_type == 'follow_up':
            subject = f"Following up re: Growth opportunities for {lead['company_name']}"
            body = f"""
            Hi Team,
            
            Just following up on my previous email about lead generation for {lead['company_name']}.
            
            We're currently offering a free lead generation assessment for qualified businesses.
            
            Would this be of interest?
            
            Best,
            AI Growth Team
            """
        
        return {'subject': subject, 'body': body}
    
    def _log_outreach(self, lead, status, error=None):
        """Log outreach activity to database"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO outreach_log (lead_id, campaign_type, status, error_message, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (lead.get('id'), 'cold_email', status, error, datetime.now()))
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Error logging outreach: {e}")
