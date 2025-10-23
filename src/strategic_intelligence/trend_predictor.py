import logging
from datetime import datetime, timedelta
from typing import Dict, List
import pandas as pd
import numpy as np

class TrendPredictor:
    def __init__(self, db_connection):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
    
    def predict_market_trends(self, historical_data: pd.DataFrame = None) -> Dict:
        """Predict future market trends"""
        self.logger.info("Predicting market trends")
        
        if historical_data is None:
            historical_data = self._generate_sample_data()
        
        predictions = {
            'timestamp': datetime.now(),
            'time_horizon': '6_months',
            'digital_adoption_trend': self._predict_digital_adoption(historical_data),
            'sme_spending_trend': self._predict_sme_spending(historical_data),
            'technology_adoption_trend': self._predict_tech_adoption(historical_data),
            'risk_factors': self._identify_risk_factors(),
            'opportunity_areas': self._identify_opportunity_areas(),
            'confidence_level': 'medium'  # low, medium, high
        }
        
        return predictions
    
    def predict_revenue_growth(self, current_clients: int, growth_rate: float = 0.3) -> Dict:
        """Predict revenue growth over next 12 months"""
        projections = {}
        monthly_clients = current_clients
        monthly_rate = 25000  # ZAR
        
        for month in range(1, 13):
            monthly_revenue = monthly_clients * monthly_rate
            cumulative_revenue = sum(proj['revenue'] for proj in projections.values()) + monthly_revenue
            
            projections[f'month_{month}'] = {
                'month': month,
                'clients': int(monthly_clients),
                'revenue': monthly_revenue,
                'cumulative_revenue': cumulative_revenue,
                'growth_rate': growth_rate
            }
            
            # Apply compounding growth
            monthly_clients *= (1 + growth_rate)
        
        summary = {
            'projections': projections,
            'total_year_revenue': projections['month_12']['cumulative_revenue'],
            'average_monthly_growth': growth_rate * 100,
            'clients_end_year': int(monthly_clients / (1 + growth_rate))  # Back to final month count
        }
        
        return summary
    
    def identify_seasonal_patterns(self) -> Dict:
        """Identify seasonal patterns in the South African market"""
        return {
            'q1_jan_mar': {
                'characteristics': ['Post-holiday planning', 'Budget allocation', 'Strategic initiatives start'],
                'opportunity': 'high',
                'recommendation': 'Focus on strategic planning and budget discussions'
            },
            'q2_apr_jun': {
                'characteristics': ['Execution phase', 'Mid-year reviews', 'Adjustment period'],
                'opportunity': 'medium', 
                'recommendation': 'Emphasize quick wins and measurable results'
            },
            'q3_jul_sep': {
                'characteristics': ['Budget planning for next year', 'Performance evaluation', 'Decision making'],
                'opportunity': 'high',
                'recommendation': 'Position for next year budgets and annual contracts'
            },
            'q4_oct_dec': {
                'characteristics': ['Year-end push', 'Budget utilization', 'Holiday slowdown'],
                'opportunity': 'medium',
                'recommendation': 'Focus on closing deals and planning for Q1'
            }
        }
    
    def _predict_digital_adoption(self, data: pd.DataFrame) -> Dict:
        """Predict digital adoption trends"""
        return {
            'trend': 'increasing',
            'rate': 'accelerating', 
            'key_drivers': ['Remote work', 'E-commerce growth', 'Mobile penetration'],
            'estimated_growth': 25,  # Percentage
            'timeframe': 'next_12_months'
        }
    
    def _predict_sme_spending(self, data: pd.DataFrame) -> Dict:
        """Predict SME spending patterns"""
        return {
            'trend': 'cautiously_increasing',
            'focus_areas': ['Digital marketing', 'Automation', 'Customer acquisition'],
            'budget_constraints': ['Economic uncertainty', 'Load shedding costs', 'Inflation'],
            'estimated_increase': 15  # Percentage
        }
    
    def _predict_tech_adoption(self, data: pd.DataFrame) -> Dict:
        """Predict technology adoption trends"""
        return {
            'ai_adoption': 'accelerating',
            'cloud_services': 'mature',
            'automation_tools': 'growing', 
            'emerging_technologies': ['AI-powered analytics', 'Predictive lead scoring', 'Conversational AI'],
            'adoption_barriers': ['Cost', 'Technical skills', 'Integration complexity']
        }
    
    def _identify_risk_factors(self) -> List[Dict]:
        """Identify potential risk factors"""
        return [
            {
                'risk': 'Economic downturn',
                'probability': 'medium',
                'impact': 'high',
                'mitigation': 'Diversify service offerings, focus on ROI demonstration'
            },
            {
                'risk': 'Increased competition', 
                'probability': 'high',
                'impact': 'medium',
                'mitigation': 'Differentiate through AI capabilities and superior service'
            },
            {
                'risk': 'Technology disruption',
                'probability': 'low', 
                'impact': 'high',
                'mitigation': 'Continuous innovation and technology monitoring'
            }
        ]
    
    def _identify_opportunity_areas(self) -> List[Dict]:
        """Identify emerging opportunity areas"""
        return [
            {
                'area': 'Vertical-specific AI solutions',
                'potential': 'high',
                'timeline': '6-12 months',
                'actions': ['Develop industry-specific templates', 'Create vertical case studies']
            },
            {
                'area': 'SMB market automation',
                'potential': 'very_high', 
                'timeline': '3-6 months',
                'actions': ['Create affordable packages', 'Simplify onboarding process']
            },
            {
                'area': 'Integrated marketing suites',
                'potential': 'medium',
                'timeline': '12-18 months', 
                'actions': ['Partner with complementary tools', 'Develop API integrations']
            }
        ]
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate sample historical data for analysis"""
        dates = pd.date_range(start='2023-01-01', end=datetime.now(), freq='M')
        data = {
            'date': dates,
            'digital_adoption': np.random.normal(60, 5, len(dates)).cumsum(),
            'sme_spending': np.random.normal(50, 8, len(dates)).cumsum(),
            'lead_demand': np.random.normal(45, 6, len(dates)).cumsum()
        }
        return pd.DataFrame(data)
