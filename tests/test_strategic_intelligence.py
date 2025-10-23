#!/usr/bin/env python3
"""
Tests for strategic intelligence components
"""

import unittest
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / 'src'))

from strategic_intelligence import MarketAnalyzer, CompetitorTracker, TrendPredictor
import sqlite3

class TestMarketAnalyzer(unittest.TestCase):
    
    def setUp(self):
        # Create in-memory database for testing
        self.db = sqlite3.connect(':memory:')
        self.market_analyzer = MarketAnalyzer(self.db)
    
    def test_analyze_sa_market(self):
        analysis = self.market_analyzer.analyze_sa_market()
        self.assertIsInstance(analysis, dict)
        self.assertIn('economic_indicators', analysis)
        self.assertIn('market_health_score', analysis)
    
    def test_get_market_share_estimate(self):
        estimates = self.market_analyzer.get_market_share_estimate(10000)
        self.assertIsInstance(estimates, dict)
        self.assertIn('market_share_estimates', estimates)

class TestCompetitorTracker(unittest.TestCase):
    
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.competitor_tracker = CompetitorTracker(self.db)
    
    def test_add_competitor(self):
        initial_count = len(self.competitor_tracker.competitors)
        self.competitor_tracker.add_competitor('test.com', 'Test Competitor', ['SEO'])
        self.assertEqual(len(self.competitor_tracker.competitors), initial_count + 1)
    
    def test_analyze_competitor_landscape(self):
        analysis = self.competitor_tracker.analyze_competitor_landscape()
        self.assertIsInstance(analysis, dict)
        self.assertIn('total_competitors', analysis)

class TestTrendPredictor(unittest.TestCase):
    
    def setUp(self):
        self.db = sqlite3.connect(':memory:')
        self.trend_predictor = TrendPredictor(self.db)
    
    def test_predict_revenue_growth(self):
        projections = self.trend_predictor.predict_revenue_growth(5, 0.3)
        self.assertIsInstance(projections, dict)
        self.assertIn('projections', projections)
    
    def test_identify_seasonal_patterns(self):
        patterns = self.trend_predictor.identify_seasonal_patterns()
        self.assertIsInstance(patterns, dict)
        self.assertIn('q1_jan_mar', patterns)

if __name__ == '__main__':
    unittest.main()
