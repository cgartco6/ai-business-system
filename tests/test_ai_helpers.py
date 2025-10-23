#!/usr/bin/env python3
"""
Tests for AI helpers components
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from ai_helpers import EmailManager, DatabaseHandler, APIClient, ReportGenerator
import sqlite3

class TestEmailManager(unittest.TestCase):
    
    def setUp(self):
        config = {
            'smtp_server': 'test.server.com',
            'smtp_port': 587,
            'username': 'test@example.com',
            'password': 'testpass',
            'use_tls': True
        }
        self.email_manager = EmailManager(config)
    
    def test_validate_email(self):
        self.assertTrue(self.email_manager.validate_email('test@example.com'))
        self.assertFalse(self.email_manager.validate_email('invalid-email'))
    
    def test_create_email_template(self):
        variables = {'name': 'John', 'company_name': 'Test Corp'}
        template = self.email_manager.create_email_template('welcome', variables)
        self.assertIsInstance(template, str)
        self.assertIn('John', template)
        self.assertIn('Test Corp', template)

class TestDatabaseHandler(unittest.TestCase):
    
    def setUp(self):
        config = {}
        self.db_handler = DatabaseHandler(config, use_sqlite=True)
        self.db_handler.connect()
    
    def test_execute_query(self):
        result = self.db_handler.execute_query("SELECT 1 as test")
        self.assertIsInstance(result, list)
    
    def test_insert_lead(self):
        lead_data = {
            'id': 'test_lead_001',
            'company_name': 'Test Company',
            'contact_email': 'test@example.com',
            'industry': 'Technology',
            'size': '10-50',
            'location': 'Test City',
            'lead_score': 7.5,
            'status': 'new',
            'priority': 'medium',
            'source': 'test'
        }
        success = self.db_handler.insert_lead(lead_data)
        self.assertTrue(success)

class TestAPIClient(unittest.TestCase):
    
    def setUp(self):
        api_keys = {'test_key': 'test_value'}
        self.api_client = APIClient(api_keys)
    
    def test_test_api_connectivity(self):
        # This is a mock test since we're not making real API calls
        connectivity = self.api_client.test_api_connectivity()
        self.assertIsInstance(connectivity, dict)
        self.assertIn('tests', connectivity)

class TestReportGenerator(unittest.TestCase):
    
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.report_generator = ReportGenerator(self.db)
    
    def test_generate_daily_report(self):
        report = self.report_generator.generate_daily_report()
        self.assertIsInstance(report, dict)
        self.assertIn('executive_summary', report)
        self.assertIn('lead_metrics', report)

if __name__ == '__main__':
    unittest.main()
