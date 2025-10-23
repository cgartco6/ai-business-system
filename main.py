#!/usr/bin/env python3
"""
AI Business System - Main Application
Optimized for Windows 10 i7 with 16GB RAM
"""

import logging
import sys
from datetime import datetime
from src.synthetic_intelligence.strategy_analyzer import StrategyAnalyzer
from src.synthetic_intelligence.decision_engine import DecisionEngine
from src.strategic_intelligence.market_analyzer import MarketAnalyzer
from src.ai_agents.lead_generator import LeadGenerator
from src.ai_agents.outreach_agent import OutreachAgent
from src.ai_helpers.email_manager import EmailManager
from src.ai_helpers.database_handler import DatabaseHandler
from config.settings import DATABASE_CONFIG, EMAIL_CONFIG, BUSINESS_CONFIG

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_business.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class AIBusinessOrchestrator:
    def __init__(self):
        self.logger = logger
        self.setup_complete = False
        
        # Initialize components
        self.db_handler = DatabaseHandler(DATABASE_CONFIG, use_sqlite=True)  # Use SQLite for local dev
        self.email_manager = EmailManager(EMAIL_CONFIG)
        
        # Core intelligence systems
        self.strategy_analyzer = StrategyAnalyzer(DATABASE_CONFIG)
        self.decision_engine = DecisionEngine()
        self.market_analyzer = MarketAnalyzer(self.db_handler.connection)
        
        # AI Agents
        self.lead_generator = LeadGenerator(self.db_handler.connection, self.email_manager)
        self.outreach_agent = OutreachAgent(self.email_manager, self.db_handler.connection)
    
    def setup(self):
        """Setup the entire system"""
        self.logger.info("Setting up AI Business System...")
        
        try:
            # Initialize database
            if not self.db_handler.connect():
                raise Exception("Database connection failed")
            
            self.setup_complete = True
            self.logger.info("AI Business System setup completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            return False
    
    def run_daily_operations(self):
        """Run daily business operations"""
        if not self.setup_complete:
            self.logger.error("System not setup. Run setup() first.")
            return
        
        self.logger.info("Starting daily operations...")
        
        try:
            # 1. Strategic Intelligence - Market Analysis
            market_analysis = self.market_analyzer.analyze_sa_market()
            self.logger.info(f"Market analysis completed: {len(market_analysis['opportunity_areas'])} opportunities found")
            
            # 2. Generate strategic insights
            strategy = self.strategy_analyzer.analyze_market_opportunity(BUSINESS_CONFIG['niche'])
            self.logger.info(f"Strategic analysis: {strategy['recommended_strategy']}")
            
            # 3. Generate leads
            leads = self.lead_generator.generate_leads(target_companies=20)
            qualified_leads = self.lead_generator.qualify_leads(leads)
            self.logger.info(f"Generated {len(leads)} leads, {len(qualified_leads)} qualified")
            
            # 4. Execute outreach
            if qualified_leads:
                outreach_results = self.outreach_agent.execute_outreach_campaign(qualified_leads)
                successful_outreach = [r for r in outreach_results if r['status'] == 'sent']
                self.logger.info(f"Outreach completed: {len(successful_outreach)}/{len(outreach_results)} successful")
            
            # 5. Make strategic decisions
            context = {
                'revenue_gap': BUSINESS_CONFIG['target_revenue'] - self._calculate_current_revenue(),
                'leads_generated_today': len(leads),
                'outreach_success_rate': len(successful_outreach) / len(outreach_results) if outreach_results else 0
            }
            
            decisions = self.decision_engine.make_strategic_decision(context, BUSINESS_CONFIG, {})
            self.logger.info(f"Strategic decisions made: {len(decisions['recommended_actions'])} actions recommended")
            
            self.logger.info("Daily operations completed successfully")
            
        except Exception as e:
            self.logger.error(f"Daily operations failed: {e}")
    
    def _calculate_current_revenue(self):
        """Calculate current monthly revenue"""
        try:
            cursor = self.db_handler.connection.cursor()
            cursor.execute("SELECT COUNT(*) as active_clients, SUM(monthly_rate) as monthly_revenue FROM clients WHERE status = 'active'")
            result = cursor.fetchone()
            return result[1] or 0 if result else 0
        except:
            return 0
    
    def generate_performance_report(self):
        """Generate performance report"""
        report = {
            'timestamp': datetime.now(),
            'leads_generated': self.lead_generator.leads_generated,
            'emails_sent': self.outreach_agent.sent_emails,
            'current_revenue': self._calculate_current_revenue(),
            'revenue_target': BUSINESS_CONFIG['target_revenue'],
            'progress_percentage': (self._calculate_current_revenue() / BUSINESS_CONFIG['target_revenue']) * 100
        }
        
        self.logger.info(f"Performance Report: R{report['current_revenue']:,.2f}/R{report['revenue_target']:,.2f} ({report['progress_percentage']:.1f}%)")
        return report

def main():
    """Main application entry point"""
    print("🚀 AI Business System Starting...")
    print("💻 Optimized for Windows 10 i7 16GB RAM")
    print("🌍 South Africa Market Focus")
    print("🎯 Target: R1,000,000/month")
    
    orchestrator = AIBusinessOrchestrator()
    
    if orchestrator.setup():
        # Run daily operations
        orchestrator.run_daily_operations()
        
        # Generate report
        report = orchestrator.generate_performance_report()
        
        print("\n" + "="*50)
        print("DAILY PERFORMANCE SUMMARY")
        print("="*50)
        print(f"Leads Generated: {orchestrator.lead_generator.leads_generated}")
        print(f"Emails Sent: {orchestrator.outreach_agent.sent_emails}")
        print(f"Current Revenue: R{report['current_revenue']:,.2f}")
        print(f"Target Revenue: R{report['revenue_target']:,.2f}")
        print(f"Progress: {report['progress_percentage']:.1f}%")
        print("="*50)
        
        if report['progress_percentage'] < 10:
            print("💡 Recommendation: Focus on client acquisition and outreach optimization")
        elif report['progress_percentage'] < 50:
            print("💡 Recommendation: Scale operations and consider hiring assistance")
        else:
            print("💡 Recommendation: Optimize for profitability and system automation")

if __name__ == "__main__":
    main()
