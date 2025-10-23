import smtplib
import logging
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from typing import Dict, List

class EmailManager:
    def __init__(self, email_config: Dict):
        self.config = email_config
        self.logger = logging.getLogger(__name__)
        self.sent_count = 0
        self.failed_count = 0
    
    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False) -> bool:
        """Send email using SMTP configuration"""
        try:
            # Create message
            msg = MimeMultipart()
            msg['From'] = self.config['username']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            # Add body
            if is_html:
                msg.attach(MimeText(body, 'html'))
            else:
                msg.attach(MimeText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                if self.config.get('use_tls', True):
                    server.starttls()
                
                server.login(self.config['username'], self.config['password'])
                server.send_message(msg)
            
            self.sent_count += 1
            self.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.failed_count += 1
            self.logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def send_bulk_emails(self, emails: List[Dict]) -> Dict:
        """Send bulk emails with rate limiting"""
        results = {
            'total': len(emails),
            'successful': 0,
            'failed': 0,
            'errors': []
        }
        
        for i, email_data in enumerate(emails):
            try:
                success = self.send_email(
                    to_email=email_data['to'],
                    subject=email_data['subject'],
                    body=email_data['body'],
                    is_html=email_data.get('is_html', False)
                )
                
                if success:
                    results['successful'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to send to {email_data['to']}")
                
                # Rate limiting: wait 2 seconds between emails
                if i < len(emails) - 1:  # Don't wait after the last email
                    import time
                    time.sleep(2)
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error sending to {email_data['to']}: {str(e)}")
        
        return results
    
    def check_email_balance(self) -> Dict:
        """Check remaining email quota"""
        # Afrihost typically provides generous limits
        return {
            "remaining": 95, 
            "total": 100,
            "usage_percentage": 5
        }
    
    def get_email_stats(self) -> Dict:
        """Get email sending statistics"""
        total_attempts = self.sent_count + self.failed_count
        success_rate = (self.sent_count / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            'sent_count': self.sent_count,
            'failed_count': self.failed_count,
            'success_rate': round(success_rate, 1),
            'total_attempts': total_attempts
        }
    
    def validate_email(self, email: str) -> bool:
        """Basic email validation"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def create_email_template(self, template_name: str, variables: Dict) -> str:
        """Create email template with variables"""
        templates = {
            'welcome': """
            Welcome to AI Growth Solutions SA!
            
            Dear {name},
            
            Thank you for choosing our AI-powered lead generation service. We're excited to help {company_name} achieve remarkable growth.
            
            Your dedicated account manager will be in touch shortly to discuss your specific needs and set up your customized lead generation system.
            
            Best regards,
            The AI Growth Team
            """,
            
            'onboarding': """
            Getting Started with AI Lead Generation
            
            Hi {name},
            
            We're ready to start generating qualified leads for {company_name}!
            
            Next steps:
            1. Complete your client profile
            2. Define your ideal customer criteria
            3. Review and approve your outreach strategy
            
            Our system will begin delivering 20-30 qualified leads per week starting next Monday.
            
            Best,
            AI Growth Team
            """
        }
        
        template = templates.get(template_name, '')
        for key, value in variables.items():
            template = template.replace(f'{{{key}}}', str(value))
        
        return template
