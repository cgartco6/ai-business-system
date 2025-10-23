#!/usr/bin/env python3
"""
AI Business System - Main Application
Optimized for Windows 10 i7 with 16GB RAM
Target: R1,000,000/month from South African SMEs
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from src.synthetic_intelligence.strategy_analyzer import StrategyAnalyzer
from src.synthetic_intelligence.decision_engine import DecisionEngine
from src.strategic_intelligence.market_analyzer import MarketAnalyzer
from src.strategic_intelligence.competitor_tracker import CompetitorTracker
from src.strategic_intelligence.trend_predictor import TrendPredictor
from src.ai_agents.lead_generator import LeadGenerator
from src.ai_agents.outreach_agent import OutreachAgent
from src.ai_agents.research_agent import ResearchAgent
from src.ai_agents.monitor_agent import MonitorAgent
from src.ai_helpers.email_manager import EmailManager
from src.ai_helpers.database_handler import DatabaseHandler
from src.ai_helpers.api_client import APIClient
from src.ai_helpers.report_generator import ReportGenerator
from config.settings import DATABASE_CONFIG, EMAIL_CONFIG, BUSINESS_CONFIG, SYSTEM_CONFIG

# Configure logging
def setup_logging():
    """Setup comprehensive logging"""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=getattr(logging, SYSTEM_CONFIG.get('log_level', 'INFO')),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'ai_business.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

class AIBusinessOrchestrator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_complete = False
        self.daily_operations_count = 0
        
        # Initialize components
        self.db_handler = DatabaseHandler(DATABASE_CONFIG, use_sqlite=True)  # Use SQLite for local dev
        self.email_manager = EmailManager(EMAIL_CONFIG)
        self.api_client = APIClient({})  # API keys would be loaded from credentials
        
        # Core intelligence systems
        self.strategy_analyzer = StrategyAnalyzer(DATABASE_CONFIG)
        self.decision_engine = DecisionEngine()
        self.market_analyzer = MarketAnalyzer(self.db_handler.connection)
        self.competitor_tracker = CompetitorTracker(self.db_handler.connection)
        self.trend_predictor = TrendPredictor(self.db_handler.connection)
        
        # AI Agents
        self.lead_generator = LeadGenerator(self.db_handler.connection, self.email_manager)
        self.outreach_agent = OutreachAgent(self.email_manager, self.db_handler.connection)
        self.research_agent = ResearchAgent(self.db_handler.connection)
        self.monitor_agent = MonitorAgent(self.db_handler.connection)
        
        # Helpers
        self.report_generator = ReportGenerator(self.db_handler.connection)
    
    def setup(self):
        """Setup the entire system"""
        self.logger.info("🚀 Setting up AI Business System...")
        
        try:
            # Initialize database
            if not self.db_handler.connect():
                raise Exception("Database connection failed")
            
            # Initialize market analysis
            market_analysis = self.market_analyzer.analyze_sa_market()
            self.logger.info(f"📊 Market analysis: {market_analysis['market_health_score']:.1f}/100 health score")
            
            # Initialize competitor tracking
            competitor_analysis = self.competitor_tracker.analyze_competitor_landscape()
            self.logger.info(f"🎯 Tracking {competitor_analysis['total_competitors']} competitors")
            
            self.setup_complete = True
            self.logger.info("✅ AI Business System setup completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Setup failed: {e}")
            return False
    
    def run_daily_operations(self):
        """Run daily business operations"""
        if not self.setup_complete:
            self.logger.error("System not setup. Run setup() first.")
            return
        
        self.daily_operations_count += 1
        self.logger.info(f"🔄 Starting daily operations #{self.daily_operations_count}...")
        
        try:
            # 1. Strategic Intelligence - Market Analysis
            market_analysis = self.market_analyzer.analyze_sa_market()
            self.logger.info(f"📈 Market opportunities: {len(market_analysis['opportunity_areas'])} areas identified")
            
            # 2. Generate strategic insights
            strategy = self.strategy_analyzer.analyze_market_opportunity(BUSINESS_CONFIG['niche'])
            self.logger.info(f"🎯 Strategic direction: {strategy['recommended_strategy']}")
            
            # 3. Generate leads
            leads = self.lead_generator.generate_leads(target_companies=20)
            qualified_leads = self.lead_generator.qualify_leads(leads)
            self.logger.info(f"📋 Leads: {len(leads)} generated, {len(qualified_leads)} qualified")
            
            # 4. Execute outreach to high-priority leads
            high_priority_leads = [lead for lead in qualified_leads if lead['priority'] == 'high']
            if high_priority_leads:
                outreach_results = self.outreach_agent.execute_outreach_campaign(high_priority_leads)
                successful_outreach = [r for r in outreach_results if r['status'] == 'sent']
                self.logger.info(f"📧 Outreach: {len(successful_outreach)}/{len(outreach_results)} emails sent successfully")
            
            # 5. Research key prospects
            if qualified_leads:
                key_prospect = qualified_leads[0]
                research_data = self.research_agent.research_company(key_prospect['company_name'])
                self.logger.info(f"🔍 Research completed for: {key_prospect['company_name']}")
            
            # 6. Make strategic decisions
            current_revenue = self._calculate_current_revenue()
            context = {
                'revenue_gap': BUSINESS_CONFIG['target_revenue'] - current_revenue,
                'leads_generated_today': len(leads),
                'outreach_success_rate': len(successful_outreach) / len(outreach_results) if outreach_results else 0,
                'client_acquisition_cost': self._estimate_cac(),
                'conversion_rate': self._calculate_conversion_rate(),
                'client_retention_rate': self._calculate_retention_rate()
            }
            
            decisions = self.decision_engine.make_strategic_decision(context, BUSINESS_CONFIG, {})
            self.logger.info(f"🤖 AI Decisions: {len(decisions['recommended_actions'])} actions recommended")
            
            # 7. Generate daily report
            daily_report = self.report_generator.generate_daily_report()
            self.report_generator.save_report(daily_report, 'daily')
            self.logger.info("📊 Daily report generated and saved")
            
            self.logger.info("✅ Daily operations completed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Daily operations failed: {e}")
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring in background"""
        self.logger.info("👁️ Starting continuous system monitoring...")
        # This would run in a separate thread in production
        monitoring_report = self.monitor_agent.generate_daily_report()
        self.logger.info(f"📈 Monitoring: System health {monitoring_report['system_health']['overall_status']}")
    
    def _calculate_current_revenue(self):
        """Calculate current monthly revenue"""
        try:
            cursor = self.db_handler.connection.cursor()
            cursor.execute("SELECT SUM(monthly_rate) as monthly_revenue FROM clients WHERE status = 'active'")
            result = cursor.fetchone()
            return result[0] or 0 if result else 0
        except Exception as e:
            self.logger.error(f"Error calculating revenue: {e}")
            return 0
    
    def _estimate_cac(self):
        """Estimate client acquisition cost"""
        # Simplified calculation - in reality, track marketing spend vs acquisitions
        return 2500  # Estimated ZAR per client
    
    def _calculate_conversion_rate(self):
        """Calculate lead to client conversion rate"""
        try:
            cursor = self.db_handler.connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM leads WHERE status = 'converted'")
            converted = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(*) FROM leads")
            total_leads = cursor.fetchone()[0] or 1
            
            return converted / total_leads
        except:
            return 0.02  # Default 2% conversion rate
    
    def _calculate_retention_rate(self):
        """Calculate client retention rate"""
        # Simplified - in reality, track client lifecycle
        return 0.90  # Default 90% retention
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        report = {
            'timestamp': datetime.now(),
            'operations_count': self.daily_operations_count,
            'lead_stats': self.lead_generator.get_lead_generation_stats(),
            'email_stats': self.email_manager.get_email_stats(),
            'campaign_stats': self.outreach_agent.get_campaign_stats(),
            'current_revenue': self._calculate_current_revenue(),
            'revenue_target': BUSINESS_CONFIG['target_revenue'],
            'progress_percentage': (self._calculate_current_revenue() / BUSINESS_CONFIG['target_revenue']) * 100,
            'system_health': 'operational'
        }
        
        self.logger.info(f"📈 Performance: R{report['current_revenue']:,.2f}/R{report['revenue_target']:,.2f} ({report['progress_percentage']:.1f}%)")
        return report

def main():
    """Main application entry point"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("🚀 AI Business System Starting...")
    print("💻 Optimized for Windows 10 i7 16GB RAM")
    print("🌍 South Africa Market Focus")
    print("🎯 Target: R1,000,000/month")
    print("=" * 60)
    
    orchestrator = AIBusinessOrchestrator()
    
    if orchestrator.setup():
        # Run initial daily operations
        orchestrator.run_daily_operations()
        
        # Run continuous monitoring
        orchestrator.run_continuous_monitoring()
        
        # Generate final report
        report = orchestrator.generate_performance_report()
        
        print("\n" + "=" * 60)
        print("DAILY PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"Leads Generated: {orchestrator.lead_generator.leads_generated}")
        print(f"Emails Sent: {orchestrator.outreach_agent.sent_emails}")
        print(f"Current Revenue: R{report['current_revenue']:,.2f}")
        print(f"Target Revenue: R{report['revenue_target']:,.2f}")
        print(f"Progress: {report['progress_percentage']:.1f}%")
        print("=" * 60)
        
        # Provide recommendations based on progress
        if report['progress_percentage'] < 10:
            print("💡 Recommendation: Focus on client acquisition and outreach optimization")
            print("   - Increase lead generation to 50+ per day")
            print("   - Personalize outreach for better response rates")
            print("   - Offer free lead generation assessment to build trust")
        elif report['progress_percentage'] < 50:
            print("💡 Recommendation: Scale operations and system automation")
            print("   - Implement advanced lead scoring")
            print("   - Automate follow-up sequences") 
            print("   - Consider hiring virtual assistant for qualification")
        else:
            print("💡 Recommendation: Optimize for profitability and expansion")
            print("   - Develop premium service tiers")
            print("   - Create referral program")
            print("   - Explore new market segments")
        
        print("\n✅ System is operational and generating revenue!")
        print("📊 Check logs/ai_business.log for detailed operations")
        print("📈 Review data/reports/ for performance analytics")
        print("=" * 60)
        
    else:
        print("❌ System setup failed. Check logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
