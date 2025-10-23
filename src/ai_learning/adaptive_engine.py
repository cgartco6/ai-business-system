import logging
import json
from datetime import datetime, timedelta
from collections import defaultdict
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd

class AdaptiveEngine:
    def __init__(self, db_connection):
        self.db = db_connection
        self.performance_data = defaultdict(list)
        self.learning_models = {}
        
    def analyze_performance_patterns(self):
        """Analyze system performance patterns for optimization"""
        try:
            # Lead generation performance
            lead_patterns = self._analyze_lead_generation_patterns()
            
            # Client conversion patterns  
            conversion_patterns = self._analyze_conversion_patterns()
            
            # Revenue optimization patterns
            revenue_patterns = self._analyze_revenue_patterns()
            
            # Generate optimization recommendations
            recommendations = self._generate_optimization_recommendations(
                lead_patterns, conversion_patterns, revenue_patterns
            )
            
            logging.info("Performance pattern analysis completed")
            return recommendations
            
        except Exception as e:
            logging.error(f"Error analyzing performance patterns: {e}")
            return []
    
    def _analyze_lead_generation_patterns(self):
        """Analyze lead generation performance patterns"""
        try:
            cursor = self.db.cursor()
            
            # Get lead data from last 30 days
            cursor.execute('''
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as lead_count,
                    AVG(lead_score) as avg_score,
                    SUM(CASE WHEN status LIKE 'qualified%' THEN 1 ELSE 0 END) as qualified_count
                FROM leads 
                WHERE created_at >= date('now', '-30 days')
                GROUP BY DATE(created_at)
                ORDER BY date
            ''')
            
            lead_data = cursor.fetchall()
            
            if not lead_data:
                return {}
            
            # Convert to pandas for analysis
            df = pd.DataFrame(lead_data, columns=['date', 'lead_count', 'avg_score', 'qualified_count'])
            df['qualification_rate'] = df['qualified_count'] / df['lead_count']
            
            patterns = {
                'avg_daily_leads': df['lead_count'].mean(),
                'avg_qualification_rate': df['qualification_rate'].mean(),
                'trend': self._calculate_trend(df['lead_count']),
                'best_performing_days': self._identify_best_days(df),
                'score_correlation': df['avg_score'].corr(df['qualification_rate'])
            }
            
            return patterns
            
        except Exception as e:
            logging.error(f"Error analyzing lead patterns: {e}")
            return {}
    
    def _analyze_conversion_patterns(self):
        """Analyze client conversion patterns"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute('''
                SELECT 
                    l.industry,
                    l.size,
                    l.lead_score,
                    CASE WHEN c.client_id IS NOT NULL THEN 1 ELSE 0 END as converted
                FROM leads l
                LEFT JOIN clients c ON l.company_name = c.company_name
                WHERE l.created_at >= date('now', '-90 days')
            ''')
            
            conversion_data = cursor.fetchall()
            
            if not conversion_data:
                return {}
            
            df = pd.DataFrame(conversion_data, columns=['industry', 'size', 'lead_score', 'converted'])
            
            # Calculate conversion rates by segment
            industry_conversion = df.groupby('industry')['converted'].mean().to_dict()
            size_conversion = df.groupby('size')['converted'].mean().to_dict()
            
            # Build simple prediction model
            X = pd.get_dummies(df[['industry', 'size']])
            y = df['converted']
            
            if len(X) > 10:  # Only build model if we have enough data
                model = LinearRegression()
                model.fit(X, y)
                self.learning_models['conversion_prediction'] = model
            
            patterns = {
                'overall_conversion_rate': df['converted'].mean(),
                'industry_conversion_rates': industry_conversion,
                'size_conversion_rates': size_conversion,
                'score_conversion_correlation': df['lead_score'].corr(df['converted'])
            }
            
            return patterns
            
        except Exception as e:
            logging.error(f"Error analyzing conversion patterns: {e}")
            return {}
    
    def _analyze_revenue_patterns(self):
        """Analyze revenue generation patterns"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute('''
                SELECT 
                    cp.service_tier,
                    cp.amount,
                    strftime('%W', cp.payment_date) as week_number,
                    c.company_name
                FROM client_payments cp
                JOIN clients c ON cp.client_id = c.id
                WHERE cp.payment_date >= date('now', '-180 days')
            ''')
            
            revenue_data = cursor.fetchall()
            
            if not revenue_data:
                return {}
            
            df = pd.DataFrame(revenue_data, columns=['service_tier', 'amount', 'week_number', 'company_name'])
            
            patterns = {
                'revenue_by_tier': df.groupby('service_tier')['amount'].sum().to_dict(),
                'avg_revenue_per_client': df.groupby('company_name')['amount'].sum().mean(),
                'weekly_revenue_trend': df.groupby('week_number')['amount'].sum().to_dict(),
                'client_retention_rate': self._calculate_retention_rate()
            }
            
            return patterns
            
        except Exception as e:
            logging.error(f"Error analyzing revenue patterns: {e}")
            return {}
    
    def _generate_optimization_recommendations(self, lead_patterns, conversion_patterns, revenue_patterns):
        """Generate actionable optimization recommendations"""
        recommendations = []
        
        # Lead generation recommendations
        if lead_patterns.get('avg_daily_leads', 0) < 20:
            recommendations.append({
                'category': 'lead_generation',
                'priority': 'high',
                'action': 'Increase lead generation efforts to reach 20+ leads daily',
                'expected_impact': '30% increase in qualified leads',
                'implementation_time': '1-2 weeks'
            })
        
        if lead_patterns.get('avg_qualification_rate', 0) < 0.3:
            recommendations.append({
                'category': 'lead_quality',
                'priority': 'medium', 
                'action': 'Improve lead qualification criteria',
                'expected_impact': 'Higher conversion rates',
                'implementation_time': '2-3 weeks'
            })
        
        # Conversion optimization
        if conversion_patterns.get('overall_conversion_rate', 0) < 0.05:
            recommendations.append({
                'category': 'conversion',
                'priority': 'high',
                'action': 'Optimize sales process and follow-up sequences',
                'expected_impact': 'Double conversion rates',
                'implementation_time': '3-4 weeks'
            })
        
        # Revenue optimization
        if revenue_patterns.get('avg_revenue_per_client', 0) < 20000:
            recommendations.append({
                'category': 'revenue',
                'priority': 'medium',
                'action': 'Implement upselling strategy to higher service tiers',
                'expected_impact': '20% increase in average revenue per client',
                'implementation_time': '4-6 weeks'
            })
        
        return recommendations
    
    def _calculate_trend(self, data):
        """Calculate trend from time series data"""
        if len(data) < 2:
            return 'stable'
        
        x = np.array(range(len(data))).reshape(-1, 1)
        y = np.array(data)
        
        model = LinearRegression()
        model.fit(x, y)
        
        slope = model.coef_[0]
        if slope > 0.1:
            return 'increasing'
        elif slope < -0.1:
            return 'decreasing'
        else:
            return 'stable'
    
    def _identify_best_days(self, df):
        """Identify best performing days of week"""
        df['day_of_week'] = pd.to_datetime(df['date']).dt.day_name()
        best_days = df.groupby('day_of_week')['lead_count'].mean().nlargest(3)
        return best_days.index.tolist()
    
    def _calculate_retention_rate(self):
        """Calculate client retention rate"""
        try:
            cursor = self.db.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(DISTINCT client_id) as total_clients,
                    COUNT(DISTINCT CASE WHEN payment_date >= date('now', '-30 days') THEN client_id END) as active_clients
                FROM client_payments
                WHERE payment_date >= date('now', '-60 days')
            ''')
            
            result = cursor.fetchone()
            if result and result[0] > 0:
                return result[1] / result[0]
            return 1.0
            
        except Exception as e:
            logging.error(f"Error calculating retention rate: {e}")
            return 1.0
    
    def predict_conversion_probability(self, lead_data):
        """Predict conversion probability for a new lead"""
        if 'conversion_prediction' not in self.learning_models:
            return 0.5  # Default probability
        
        try:
            model = self.learning_models['conversion_prediction']
            # Prepare features for prediction
            # This would need to match the training data format
            prediction = model.predict([lead_data])[0]
            return max(0, min(1, prediction))  # Clamp between 0 and 1
            
        except Exception as e:
            logging.error(f"Error predicting conversion: {e}")
            return 0.5
