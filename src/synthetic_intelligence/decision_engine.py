import logging
from datetime import datetime
from typing import Dict, List
import json

class DecisionEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.decision_history = []
        self.performance_metrics = {}
    
    def make_strategic_decision(self, context: Dict, goals: Dict, constraints: Dict) -> Dict:
        """Make strategic business decisions using rule-based AI"""
        self.logger.info("Making strategic decision based on current context")
        
        decision = {
            'timestamp': datetime.now(),
            'context': context,
            'recommended_actions': [],
            'expected_impact': '',
            'risk_level': 'medium',
            'priority': 'medium',
            'estimated_effort': 'medium'
        }
        
        # Revenue gap analysis
        revenue_gap = context.get('revenue_gap', 0)
        if revenue_gap > 500000:
            decision['recommended_actions'].extend([
                {
                    'action': "Increase outreach capacity by 50%",
                    'impact': "high",
                    'timeline': "immediate"
                },
                {
                    'action': "Launch referral program for existing clients",
                    'impact': "medium",
                    'timeline': "1-2 weeks"
                },
                {
                    'action': "Create limited-time premium package offer",
                    'impact': "high", 
                    'timeline': "1 week"
                }
            ])
            decision['expected_impact'] = "High - Potential to close 40-60% of revenue gap"
            decision['priority'] = 'high'
        
        # Client acquisition cost optimization
        cac = context.get('client_acquisition_cost', 0)
        if cac > 5000:
            decision['recommended_actions'].append({
                'action': "Optimize lead qualification process to focus on high-intent prospects",
                'impact': "medium",
                'timeline': "2-3 weeks"
            })
        
        # Lead conversion rate optimization
        conversion_rate = context.get('conversion_rate', 0)
        if conversion_rate < 0.05:  # Less than 5%
            decision['recommended_actions'].append({
                'action': "Improve email personalization and follow-up sequence",
                'impact': "high",
                'timeline': "1 week"
            })
        
        # Client retention focus
        retention_rate = context.get('client_retention_rate', 1.0)
        if retention_rate < 0.85:  # Less than 85%
            decision['recommended_actions'].append({
                'action': "Implement client success check-ins and value demonstration",
                'impact': "high", 
                'timeline': "immediate"
            })
        
        self.decision_history.append(decision)
        self.logger.info(f"Strategic decision made: {len(decision['recommended_actions'])} actions recommended")
        
        return decision
    
    def evaluate_agent_performance(self, agent_metrics: Dict) -> List[str]:
        """Evaluate and optimize AI agent performance"""
        recommendations = []
        
        for agent, metrics in agent_metrics.items():
            success_rate = metrics.get('success_rate', 0)
            response_time = metrics.get('response_time', 999)
            error_rate = metrics.get('error_rate', 0)
            
            if success_rate < 0.3:
                recommendations.append(f"Retrain {agent} with new data and patterns")
            
            if response_time > 60:  # seconds
                recommendations.append(f"Optimize {agent} algorithms for better performance")
            
            if error_rate > 0.1:  # 10% error rate
                recommendations.append(f"Add error handling and validation to {agent}")
        
        return recommendations
    
    def prioritize_actions(self, actions: List[Dict]) -> List[Dict]:
        """Prioritize actions based on impact and effort"""
        scored_actions = []
        
        for action in actions:
            # Simple scoring: impact (3 points) vs effort (1 point)
            impact_scores = {'low': 1, 'medium': 2, 'high': 3}
            effort_scores = {'low': 3, 'medium': 2, 'high': 1}
            
            score = (impact_scores.get(action.get('impact', 'medium'), 2) * 3 + 
                    effort_scores.get(action.get('estimated_effort', 'medium'), 2))
            
            scored_actions.append({
                **action,
                'priority_score': score
            })
        
        # Sort by priority score descending
        return sorted(scored_actions, key=lambda x: x['priority_score'], reverse=True)
    
    def get_decision_history(self) -> List[Dict]:
        """Get decision history"""
        return self.decision_history
