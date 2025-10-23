import logging
import random
from datetime import datetime
from typing import Dict, List

class ContentGenerator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict:
        """Load content templates"""
        return {
            'email_subjects': [
                "Growth opportunity for {company_name}",
                "How {company_name} can generate more leads",
                "AI-powered lead generation for {company_name}",
                "Increasing {company_name}'s qualified leads",
                "Digital transformation for {company_name}"
            ],
            'value_propositions': [
                "Generate 20-30 qualified leads weekly",
                "3x increase in qualified leads within 30 days",
                "AI-powered system working 24/7 for your business",
                "Proven results with South African SMEs",
                "No upfront costs, pay only for results"
            ]
        }
    
    def generate_email_subject(self, company_data: Dict) -> str:
        """Generate personalized email subject"""
        template = random.choice(self.templates['email_subjects'])
        return template.format(**company_data)
    
    def generate_email_body(self, lead_data: Dict, email_type: str = 'cold') -> str:
        """Generate personalized email body"""
        if email_type == 'cold':
            return self._generate_cold_email(lead_data)
        elif email_type == 'follow_up':
            return self._generate_follow_up_email(lead_data)
        else:
            return self._generate_cold_email(lead_data)
    
    def _generate_cold_email(self, lead_data: Dict) -> str:
        """Generate cold email content"""
        return f"""
Dear {lead_data.get('contact_name', 'Team')} at {lead_data['company_name']},

I came across {lead_data['company_name']} and was impressed by your work in the {lead_data.get('industry', 'industry')} sector.

We specialize in helping businesses like yours generate 20-30 qualified leads per week using our AI-powered systems. Many of our clients in South Africa are achieving remarkable results, with some seeing 3x increases in qualified leads within the first month.

Our system works 24/7 to:
• Identify high-intent potential customers
• Qualify leads based on your specific criteria
• Deliver ready-to-contact prospects directly to you

Would you be open to a quick 15-minute call to explore if similar results would be valuable for {lead_data['company_name']}?

Best regards,
AI Growth Team
AI Growth Solutions SA
        """
    
    def _generate_follow_up_email(self, lead_data: Dict) -> str:
        """Generate follow-up email content"""
        return f"""
Hi {lead_data.get('contact_name', 'Team')},

Just following up on my previous email about lead generation opportunities for {lead_data['company_name']}.

We're currently offering a free lead generation assessment for qualified businesses. This includes:
- Analysis of your current lead flow
- Identification of 3-5 immediate opportunities
- Customized AI lead generation strategy

Would this be of interest?

Best,
AI Growth Team
        """
    
    def generate_value_proposition(self) -> str:
        """Generate value proposition"""
        return random.choice(self.templates['value_propositions'])
