import time
import random
from datetime import datetime
import logging
from src.ai_helpers.email_manager import EmailManager

class LeadGenerator:
    def __init__(self, db_connection, email_manager):
        self.db = db_connection
        self.email_manager = email_manager
        self.leads_generated = 0
        self.logger = logging.getLogger(__name__)
    
    def generate_leads(self, target_companies=50):
        """Generate leads from target companies"""
        leads = []
        
        # Simulate finding companies that might need services
        # In reality, this would use LinkedIn API, company directories, etc.
        sample_companies = self._get_sample_companies()
        
        for company in sample_companies[:target_companies]:
            lead = {
                'company_name': company['name'],
                'contact_email': company.get('email', f"info@{company['name'].lower().replace(' ', '')}.co.za"),
                'industry': company['industry'],
                'size': company['size'],
                'lead_score': self._calculate_lead_score(company),
                'generated_at': datetime.now(),
                'status': 'new'
            }
            leads.append(lead)
            self.leads_generated += 1
        
        self._save_leads_to_db(leads)
        return leads
    
    def qualify_leads(self, leads):
        """Qualify leads based on scoring"""
        qualified_leads = []
        
        for lead in leads:
            if lead['lead_score'] >= 7:  # High priority
                lead['priority'] = 'high'
                qualified_leads.append(lead)
            elif lead['lead_score'] >= 5:  # Medium priority
                lead['priority'] = 'medium'
                qualified_leads.append(lead)
        
        return qualified_leads
    
    def _get_sample_companies(self):
        """Get sample South African companies for testing"""
        return [
            {'name': 'Tech Solutions SA', 'industry': 'Technology', 'size': '10-50', 'location': 'Johannesburg'},
            {'name': 'Digital Marketing Pros', 'industry': 'Marketing', 'size': '5-20', 'location': 'Cape Town'},
            {'name': 'Business Consultants CT', 'industry': 'Consulting', 'size': '10-30', 'location': 'Cape Town'},
            {'name': 'SA Ecommerce Store', 'industry': 'Retail', 'size': '15-40', 'location': 'Durban'},
            {'name': 'Innovation Labs SA', 'industry': 'Technology', 'size': '20-100', 'location': 'Pretoria'}
        ]
    
    def _calculate_lead_score(self, company):
        """Calculate lead score based on company attributes"""
        score = 5  # Base score
        
        # Industry multiplier
        if company['industry'].lower() in ['technology', 'marketing', 'consulting']:
            score += 2
        
        # Size multiplier
        if company['size'] == '10-50':
            score += 1
        elif company['size'] == '20-100':
            score += 2
        
        # Location multiplier
        if company['location'] in ['Johannesburg', 'Cape Town']:
            score += 1
        
        return min(score, 10)  # Cap at 10
    
    def _save_leads_to_db(self, leads):
        """Save leads to database"""
        try:
            cursor = self.db.cursor()
            for lead in leads:
                cursor.execute('''
                    INSERT INTO leads (company_name, contact_email, industry, size, lead_score, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (lead['company_name'], lead['contact_email'], lead['industry'], 
                      lead['size'], lead['lead_score'], lead['status'], lead['generated_at']))
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Error saving leads to DB: {e}")
