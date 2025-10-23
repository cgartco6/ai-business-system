#!/usr/bin/env python3
"""
Tests for synthetic intelligence components
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from synthetic_intelligence import ContentGenerator, StrategyAnalyzer, DecisionEngine

class TestContentGenerator(unittest.TestCase):
    
    def setUp(self):
        self.content_gen = ContentGenerator()
    
    def test_generate_email_subject(self):
        company_data = {'company_name': 'Test Company'}
        subject = self.content_gen.generate_email_subject(company_data)
        self.assertIsInstance(subject, str)
        self.assertIn('Test Company', subject)
    
    def test_generate_email_body(self):
        lead_data = {
            'company_name': 'Test Company',
            'contact_name': 'John Doe',
            'industry': 'Technology'
        }
        body = self.content_gen.generate_email_body(lead_data, 'cold')
        self.assertIsInstance(body, str)
        self.assertIn('Test Company', body)

class TestStrategyAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.strategy_analyzer = StrategyAnalyzer({})
    
    def test_analyze_market_opportunity(self):
        analysis = self.strategy_analyzer.analyze_market_opportunity('Technology')
        self.assertIsInstance(analysis, dict)
        self.assertIn('market_size', analysis)
        self.assertIn('recommended_strategy', analysis)
    
    def test_estimate_market_size(self):
        market_size = self.strategy_analyzer._estimate_market_size('Technology')
        self.assertIsInstance(market_size, int)
        self.assertGreater(market_size, 0)

class TestDecisionEngine(unittest.TestCase):
    
    def setUp(self):
        self.decision_engine = DecisionEngine()
    
    def test_make_strategic_decision(self):
        context = {'revenue_gap': 600000}
        goals = {'target_revenue': 1000000}
        constraints = {}
        
        decision = self.decision_engine.make_strategic_decision(context, goals, constraints)
        self.assertIsInstance(decision, dict)
        self.assertIn('recommended_actions', decision)
    
    def test_evaluate_agent_performance(self):
        agent_metrics = {
            'lead_generator': {'success_rate': 0.2, 'response_time': 70, 'error_rate': 0.15}
        }
        recommendations = self.decision_engine.evaluate_agent_performance(agent_metrics)
        self.assertIsInstance(recommendations, list)

if __name__ == '__main__':
    unittest.main()
