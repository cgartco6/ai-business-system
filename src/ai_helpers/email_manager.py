import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import logging

class EmailManager:
    def __init__(self, email_config):
        self.config = email_config
        self.logger = logging.getLogger(__name__)
    
    def send_email(self, to_email, subject, body, is_html=False):
        """Send email using Afrihost SMTP"""
        try:
            msg = MimeMultipart()
            msg['From'] = self.config['username']
            msg['To'] = to_email
            msg['Subject'] = subject
            
            if is_html:
                msg.attach(MimeText(body, 'html'))
            else:
                msg.attach(MimeText(body, 'plain'))
            
            with smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port']) as server:
                server.starttls()
                server.login(self.config['username'], self.config['password'])
                server.send_message(msg)
            
            self.logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {e}")
            return False
    
    def check_email_balance(self):
        """Check remaining email quota"""
        # Afrihost typically provides generous limits
        return {"remaining": 95, "total": 100}  # Example
