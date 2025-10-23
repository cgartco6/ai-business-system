import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, List
import json

class MarketAnalyzer:
    def __init__(self, db_connection):
        self.db = db_connection
        self.cache = {}
        self.logger = logging.getLogger(__name__)
    
    def analyze_sa_market(self) -> Dict:
        """Analyze South African market conditions for digital services"""
        self.logger.info("Analyzing South African market conditions")
        
        analysis = {
            'timestamp': datetime.now(),
            'economic_indicators': self._get_economic_indicators(),
            'digital_adoption_trends': self._get_digital_trends(),
            'sme_sentiment': self._get_sme_sentiment(),
            'opportunity_areas': [],
            'market_health_score': 0,
            'recommendations': []
        }
        
        # Calculate market health score (0-100)
        economic_score = analysis['economic_indicators']['business_confidence'] / 100 * 25
        digital_score = analysis['digital_adoption_trends']['internet_penetration'] / 100 * 25
        sentiment_score = analysis['sme_sentiment']['optimism'] / 100 * 25
        growth_score = min(analysis['digital_adoption_trends']['ecommerce_growth'] / 50 * 25, 25)
        
        analysis['market_health_score'] = economic_score + digital_score + sentiment_score + growth_score
        
        # Identify high-opportunity areas
        if analysis['digital_adoption_trends'].get('growth_rate', 0) > 15:
            analysis['opportunity_areas'].append({
                'area': 'Digital transformation services',
                'potential': 'high',
                'rationale': 'Rapid digital adoption creates demand for AI solutions'
            })
        
        if analysis['sme_sentiment'].get('optimism', 0) > 60:
            analysis['opportunity_areas'].append({
                'area': 'Growth and expansion services', 
                'potential': 'medium',
                'rationale': 'Positive SME sentiment indicates willingness to invest'
            })
        
        if analysis['economic_indicators'].get('inflation', 0) < 6:
            analysis['opportunity_areas'].append({
                'area': 'Cost optimization services',
                'potential': 'medium', 
                'rationale': 'Stable economy supports business investment'
            })
        
        # Generate recommendations
        if analysis['market_health_score'] > 70:
            analysis['recommendations'].append("Aggressive market expansion recommended")
        elif analysis['market_health_score'] > 50:
            analysis['recommendations'].append("Moderate growth with careful monitoring")
        else:
            analysis['recommendations'].append("Focus on niche markets and cost efficiency")
        
        self.logger.info(f"Market analysis completed. Health score: {analysis['market_health_score']:.1f}")
        return analysis
    
    def track_competitor_strategy(self, competitor_domains: List[str]) -> Dict:
        """Track competitor strategies and pricing"""
        self.logger.info(f"Tracking strategies for {len(competitor_domains)} competitors")
        
        strategies = {}
        
        for domain in competitor_domains:
            try:
                strategy = self._analyze_competitor_strategy(domain)
                strategies[domain] = strategy
                self.logger.debug(f"Analyzed competitor: {domain}")
            except Exception as e:
                self.logger.error(f"Error analyzing {domain}: {e}")
                strategies[domain] = {'error': str(e)}
        
        return strategies
    
    def get_market_share_estimate(self, total_market_size: int) -> Dict:
        """Estimate potential market share"""
        # Conservative estimates for South African market
        tiers = {
            'conservative': total_market_size * 0.01,  # 1% market share
            'realistic': total_market_size * 0.03,     # 3% market share  
            'optimistic': total_market_size * 0.05     # 5% market share
        }
        
        return {
            'total_addressable_market': total_market_size,
            'market_share_estimates': tiers,
            'estimated_monthly_revenue': {
                tier: share * 25000 for tier, share in tiers.items()  # R25,000 per client
            }
        }
    
    def _get_economic_indicators(self) -> Dict:
        """Get South African economic indicators"""
        # Mock data - integrate with Stats SA or similar APIs
        return {
            'gdp_growth': 0.8,           # Percentage
            'inflation': 5.2,            # Percentage
            'business_confidence': 45,    # Index (0-100)
            'unemployment': 32.7,         # Percentage
            'interest_rate': 8.25         # Percentage
        }
    
    def _get_digital_trends(self) -> Dict:
        """Get digital adoption trends in South Africa"""
        return {
            'internet_penetration': 72,      # Percentage
            'mobile_usage': 85,              # Percentage  
            'ecommerce_growth': 25,          # Percentage year-on-year
            'digital_marketing_adoption': 60, # Percentage of businesses
            'saas_adoption': 35,             # Percentage of businesses
            'growth_rate': 20                # Overall digital growth rate
        }
    
    def _get_sme_sentiment(self) -> Dict:
        """Get SME business sentiment in South Africa"""
        return {
            'optimism': 65,              # Percentage optimistic about future
            'investment_intent': 55,      # Percentage planning to invest
            'hiring_plans': 40,           # Percentage planning to hire
            'digital_transformation_priority': 70,  # Percentage prioritizing digital
            'challenges': ['Load shedding', 'Economic uncertainty', 'Access to funding']
        }
    
    def _analyze_competitor_strategy(self, domain: str) -> Dict:
        """Analyze individual competitor strategy"""
        # Mock analysis - integrate with web scraping in production
        return {
            'pricing_range': 'R15,000 - R30,000',
            'service_focus': 'Lead generation and digital marketing',
            'market_position': 'Mid-market SME focus',
            'strengths': ['Established brand', 'Case studies', 'Multiple service offerings'],
            'weaknesses': ['Higher pricing', 'Less personalized service', 'Slower response times'],
            'differentiation_opportunities': [
                'AI-powered personalization',
                'Faster lead delivery', 
                'More flexible pricing',
                'Better customer support'
            ]
        }
