#!/usr/bin/env python3
"""
Tests for AI agents components
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from ai_agents import LeadGenerator, OutreachAgent
from ai_helpers import EmailManager, DatabaseHandler
import sqlite3

class TestLeadGenerator(unittest.TestCase):
    
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        email_config = {
            'smtp_server': 'test',
            'username': 'test',
            'password': 'test'
        }
        email_manager = EmailManager(email_config)
        self.lead_generator = LeadGenerator(self.db, email_manager)
    
    def test_generate_leads(self):
        leads = self.lead_generator.generate_leads(target_companies=5)
        self.assertIsInstance(leads, list)
        self.assertLessEqual(len(leads), 5)
        
        if leads:
            lead = leads[0]
            self.assertIn('company_name', lead)
            self.assertIn('lead_score', lead)
    
    def test_qualify_leads(self):
        # First generate some leads
        leads = self.lead_generator.generate_leads(target_companies=3)
        qualified_leads = self.lead_generator.qualify_leads(leads)
        self.assertIsInstance(qualified_leads, list)

class TestOutreachAgent(unittest.TestCase):
    
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        email_config = {
            'smtp_server': 'test',
            'username': 'test', 
            'password': 'test'
        }
        email_manager = EmailManager(email_config)
        self.outreach_agent = OutreachAgent(email_manager, self.db)
    
    def test_create_follow_up_sequence(self):
        lead = {'id': 'test_lead', 'company_name': 'Test Company'}
        follow_ups = self.outreach_agent.create_follow_up_sequence(lead, '2024-01-01')
        self.assertIsInstance(follow_ups, list)
        
        if follow_ups:
            follow_up = follow_ups[0]
            self.assertIn('days_after_initial', follow_up)
            self.assertIn('type', follow_up)

if __name__ == '__main__':
    unittest.main()
