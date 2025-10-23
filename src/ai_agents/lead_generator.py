import time
import random
from datetime import datetime
import logging
from typing import Dict, List
from src.ai_helpers.email_manager import EmailManager

class LeadGenerator:
    def __init__(self, db_connection, email_manager: EmailManager):
        self.db = db_connection
        self.email_manager = email_manager
        self.leads_generated = 0
        self.logger = logging.getLogger(__name__)
        self.sa_companies = self._load_sa_companies()
    
    def generate_leads(self, target_companies: int = 50) -> List[Dict]:
        """Generate leads from target companies"""
        self.logger.info(f"Generating {target_companies} leads")
        
        leads = []
        companies_to_process = min(target_companies, len(self.sa_companies))
        
        for i in range(companies_to_process):
            company = self.sa_companies[i]
            lead = {
                'id': f"lead_{self.leads_generated + 1:06d}",
                'company_name': company['name'],
                'contact_email': company.get('email', f"info@{company['name'].lower().replace(' ', '').replace('&', 'and')}.co.za"),
                'contact_name': company.get('contact', 'Marketing Manager'),
                'industry': company['industry'],
                'size': company['size'],
                'location': company['location'],
                'lead_score': self._calculate_lead_score(company),
                'generated_at': datetime.now(),
                'status': 'new',
                'priority': 'medium',
                'source': 'ai_generated'
            }
            leads.append(lead)
            self.leads_generated += 1
        
        self._save_leads_to_db(leads)
        self.logger.info(f"Generated {len(leads)} new leads")
        return leads
    
    def qualify_leads(self, leads: List[Dict]) -> List[Dict]:
        """Qualify leads based on scoring and business rules"""
        qualified_leads = []
        
        for lead in leads:
            # Update lead score based on additional qualification
            lead_score = self._calculate_detailed_lead_score(lead)
            lead['qualified_score'] = lead_score
            lead['last_qualified_at'] = datetime.now()
            
            if lead_score >= 8:  # High priority
                lead['priority'] = 'high'
                lead['status'] = 'qualified_high'
                qualified_leads.append(lead)
            elif lead_score >= 6:  # Medium priority
                lead['priority'] = 'medium' 
                lead['status'] = 'qualified_medium'
                qualified_leads.append(lead)
            elif lead_score >= 4:  # Low priority
                lead['priority'] = 'low'
                lead['status'] = 'qualified_low'
                # We might still track these but not prioritize outreach
        
        self.logger.info(f"Qualified {len(qualified_leads)} out of {len(leads)} leads")
        return qualified_leads
    
    def _load_sa_companies(self) -> List[Dict]:
        """Load sample South African companies"""
        return [
            {'name': 'Tech Solutions SA', 'industry': 'Technology', 'size': '10-50', 'location': 'Johannesburg', 'contact': 'CEO'},
            {'name': 'Digital Marketing Pros', 'industry': 'Marketing', 'size': '5-20', 'location': 'Cape Town', 'contact': 'Marketing Director'},
            {'name': 'Business Consultants CT', 'industry': 'Consulting', 'size': '10-30', 'location': 'Cape Town', 'contact': 'Managing Partner'},
            {'name': 'SA Ecommerce Store', 'industry': 'Retail', 'size': '15-40', 'location': 'Durban', 'contact': 'Operations Manager'},
            {'name': 'Innovation Labs SA', 'industry': 'Technology', 'size': '20-100', 'location': 'Pretoria', 'contact': 'CTO'},
            {'name': 'Financial Advisors SA', 'industry': 'Finance', 'size': '5-15', 'location': 'Johannesburg', 'contact': 'Partner'},
            {'name': 'Healthcare Solutions', 'industry': 'Healthcare', 'size': '10-25', 'location': 'Cape Town', 'contact': 'Practice Manager'},
            {'name': 'Legal Experts Inc', 'industry': 'Legal', 'size': '8-20', 'location': 'Johannesburg', 'contact': 'Senior Partner'},
            {'name': 'Construction Pros SA', 'industry': 'Construction', 'size': '15-50', 'location': 'Durban', 'contact': 'Project Director'},
            {'name': 'Hospitality Group', 'industry': 'Hospitality', 'size': '20-80', 'location': 'Cape Town', 'contact': 'General Manager'}
        ]
    
    def _calculate_lead_score(self, company: Dict) -> int:
        """Calculate basic lead score based on company attributes"""
        score = 5  # Base score
        
        # Industry multiplier
        industry_multipliers = {
            'Technology': 2,
            'Marketing': 2, 
            'Consulting': 1,
            'Finance': 1,
            'Healthcare': 1,
            'Legal': 1,
            'Retail': 1,
            'Construction': 0,
            'Hospitality': 0
        }
        score += industry_multipliers.get(company['industry'], 0)
        
        # Size multiplier
        size_scores = {
            '1-5': 0, '5-20': 1, '10-50': 2, '20-100': 3, '100+': 2
        }
        score += size_scores.get(company['size'], 1)
        
        # Location multiplier
        if company['location'] in ['Johannesburg', 'Cape Town']:
            score += 1
        
        return min(score, 10)  # Cap at 10
    
    def _calculate_detailed_lead_score(self, lead: Dict) -> float:
        """Calculate detailed lead score with more factors"""
        score = lead.get('lead_score', 5)
        
        # Contact role multiplier
        contact_roles = {
            'CEO': 1.5, 'CTO': 1.3, 'Marketing Director': 1.4, 
            'Managing Partner': 1.2, 'Operations Manager': 1.1
        }
        contact_multiplier = contact_roles.get(lead.get('contact_name', ''), 1.0)
        
        # Industry growth potential
        growth_industries = ['Technology', 'Marketing', 'Finance', 'Healthcare']
        if lead.get('industry') in growth_industries:
            score += 1
        
        # Company size potential
        if lead.get('size') in ['10-50', '20-100']:
            score += 1
        
        return min(score * contact_multiplier, 10.0)
    
    def _save_leads_to_db(self, leads: List[Dict]):
        """Save leads to database"""
        try:
            cursor = self.db.cursor()
            for lead in leads:
                cursor.execute('''
                    INSERT OR REPLACE INTO leads 
                    (id, company_name, contact_email, contact_name, industry, size, location, lead_score, status, priority, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    lead['id'], lead['company_name'], lead['contact_email'], 
                    lead.get('contact_name', ''), lead['industry'], lead['size'],
                    lead['location'], lead['lead_score'], lead['status'],
                    lead['priority'], lead['source'], lead['generated_at']
                ))
            self.db.commit()
            self.logger.info(f"Saved {len(leads)} leads to database")
        except Exception as e:
            self.logger.error(f"Error saving leads to DB: {e}")
    
    def get_lead_generation_stats(self) -> Dict:
        """Get lead generation statistics"""
        try:
            cursor = self.db.cursor()
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_leads,
                    COUNT(CASE WHEN status LIKE 'qualified%' THEN 1 END) as qualified_leads,
                    COUNT(CASE WHEN priority = 'high' THEN 1 END) as high_priority_leads,
                    AVG(lead_score) as avg_lead_score
                FROM leads
            ''')
            result = cursor.fetchone()
            
            return {
                'total_leads_generated': self.leads_generated,
                'total_in_database': result[0] if result else 0,
                'qualified_leads': result[1] if result else 0,
                'high_priority_leads': result[2] if result else 0,
                'average_lead_score': round(result[3], 2) if result and result[3] else 0
            }
        except Exception as e:
            self.logger.error(f"Error getting lead stats: {e}")
            return {}
