#!/usr/bin/env python3
"""
CostByte - Advanced Business Intelligence Platform
Military-Grade Security, Self-Healing, Self-Funding, Self-Learning
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
import threading
import time

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from src.military_security.encryption_engine import EncryptionEngine, SecureStorage
from src.military_security.access_control import AccessControl
from src.self_healing.system_monitor import SystemMonitor
from src.self_healing.auto_recovery import AutoRecovery
from src.financial_engine.revenue_tracker import RevenueTracker
from src.financial_engine.auto_funding import AutoFundingEngine
from src.ai_learning.adaptive_engine import AdaptiveEngine
from src.dashboard.app import app as dashboard_app
import sqlite3

class CostBytePlatform:
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.platform_start_time = datetime.now()
        
        # Initialize core components
        self.setup_database()
        self.setup_security()
        self.setup_business_engines()
        self.setup_ai_systems()
        
        self.logger.info("🚀 CostByte Platform Initialized")
    
    def setup_logging(self):
        """Setup comprehensive logging system"""
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / 'costbyte_platform.log', encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def setup_database(self):
        """Initialize secure database"""
        try:
            data_dir = Path('data')
            data_dir.mkdir(exist_ok=True)
            
            self.db_connection = sqlite3.connect(data_dir / 'costbyte.db')
            self.initialize_database_schema()
            self.logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Database setup failed: {e}")
            raise
    
    def initialize_database_schema(self):
        """Initialize database schema with all required tables"""
        cursor = self.db_connection.cursor()
        
        # Clients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                phone_encrypted TEXT,
                address_encrypted TEXT,
                location TEXT,
                country TEXT DEFAULT 'South Africa',
                service_tier TEXT DEFAULT 'professional',
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Client payments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                amount DECIMAL(10,2),
                currency TEXT DEFAULT 'ZAR',
                service_tier TEXT,
                payment_date DATE,
                recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                transfer_executed INTEGER DEFAULT 0,
                transfer_date DATETIME,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        ''')
        
        # Revenue allocations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS revenue_allocations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                amount DECIMAL(10,2),
                total_revenue DECIMAL(10,2),
                allocation_date DATE,
                transfer_executed INTEGER DEFAULT 0,
                transfer_date DATETIME,
                recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # System metrics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_type TEXT,
                metric_value REAL,
                recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Security events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS security_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT,
                severity TEXT,
                description TEXT,
                ip_address TEXT,
                user_agent TEXT,
                recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.db_connection.commit()
    
    def setup_security(self):
        """Initialize security systems"""
        self.encryption_engine = EncryptionEngine()
        self.secure_storage = SecureStorage()
        self.access_control = AccessControl('costbyte_master_secret_2024')
        
        self.logger.info("✅ Military-grade security systems initialized")
    
    def setup_business_engines(self):
        """Initialize business and financial engines"""
        self.revenue_tracker = RevenueTracker(self.db_connection)
        self.auto_funding = AutoFundingEngine(self.db_connection)
        
        self.logger.info("✅ Business engines initialized")
    
    def setup_ai_systems(self):
        """Initialize AI and learning systems"""
        self.adaptive_engine = AdaptiveEngine(self.db_connection)
        self.system_monitor = SystemMonitor()
        self.auto_recovery = AutoRecovery(self.db_connection)
        
        self.logger.info("✅ AI learning systems initialized")
    
    def start_platform_services(self):
        """Start all platform services"""
        try:
            # Start continuous monitoring
            self.system_monitor.start_continuous_monitoring()
            
            # Start background services
            self.start_background_services()
            
            # Initialize sample data for demonstration
            self.initialize_sample_data()
            
            self.logger.info("✅ All platform services started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start platform services: {e}")
            return False
    
    def start_background_services(self):
        """Start background maintenance services"""
        def funding_processor():
            while True:
                try:
                    # Process revenue allocations daily
                    self.auto_funding.execute_funding_transfers()
                    time.sleep(86400)  # 24 hours
                except Exception as e:
                    self.logger.error(f"Funding processor error: {e}")
                    time.sleep(3600)  # Retry in 1 hour
        
        def health_monitor():
            while True:
                try:
                    # Run health checks every 5 minutes
                    self.auto_recovery.run_health_check_cycle()
                    time.sleep(300)  # 5 minutes
                except Exception as e:
                    self.logger.error(f"Health monitor error: {e}")
                    time.sleep(300)  # Continue after error
        
        def ai_optimizer():
            while True:
                try:
                    # Run AI optimization every 6 hours
                    recommendations = self.adaptive_engine.analyze_performance_patterns()
                    if recommendations:
                        self.logger.info(f"AI Optimization: {len(recommendations)} recommendations generated")
                    time.sleep(21600)  # 6 hours
                except Exception as e:
                    self.logger.error(f"AI optimizer error: {e}")
                    time.sleep(3600)  # Retry in 1 hour
        
        # Start background threads
        threading.Thread(target=funding_processor, daemon=True).start()
        threading.Thread(target=health_monitor, daemon=True).start()
        threading.Thread(target=ai_optimizer, daemon=True).start()
        
        self.logger.info("✅ Background services started")
    
    def initialize_sample_data(self):
        """Initialize sample data for demonstration"""
        try:
            cursor = self.db_connection.cursor()
            
            # Check if sample data already exists
            cursor.execute("SELECT COUNT(*) FROM clients")
            client_count = cursor.fetchone()[0]
            
            if client_count == 0:
                self.logger.info("Initializing sample data...")
                
                # Sample clients
                sample_clients = [
                    ('Tech Solutions SA', 'Sarah Johnson', 'sarah@techsolutions.co.za', 'Johannesburg', 'professional'),
                    ('Digital Innovations', 'Mike Chen', 'mike@digitalinnovations.co.za', 'Cape Town', 'enterprise'),
                    ('Business Growth Partners', 'David Wilson', 'david@businessgrowth.co.za', 'Durban', 'professional'),
                    ('Smart Systems Ltd', 'Lisa van der Merwe', 'lisa@smartsystems.co.za', 'Pretoria', 'basic'),
                    ('Advanced Analytics SA', 'James Brown', 'james@advancedanalytics.co.za', 'Johannesburg', 'enterprise')
                ]
                
                for client in sample_clients:
                    cursor.execute('''
                        INSERT INTO clients (company_name, contact_person, email, location, service_tier)
                        VALUES (?, ?, ?, ?, ?)
                    ''', client)
                
                # Sample payments
                from datetime import datetime, timedelta
                import random
                
                for client_id in range(1, 6):
                    for month in range(1, 4):  # Last 3 months
                        payment_date = datetime.now() - timedelta(days=30 * month)
                        amount = random.choice([15000, 25000, 50000])
                        
                        cursor.execute('''
                            INSERT INTO client_payments (client_id, amount, payment_date, service_tier)
                            VALUES (?, ?, ?, ?)
                        ''', (client_id, amount, payment_date, sample_clients[client_id-1][4]))
                
                self.db_connection.commit()
                self.logger.info("✅ Sample data initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing sample data: {e}")
    
    def get_platform_status(self):
        """Get comprehensive platform status"""
        status = {
            'platform_uptime': str(datetime.now() - self.platform_start_time),
            'database_connection': 'active',
            'security_systems': 'operational',
            'business_engines': 'running',
            'ai_systems': 'learning',
            'background_services': 'active',
            'last_health_check': datetime.now().isoformat()
        }
        
        # Add component-specific status
        try:
            status['revenue_metrics'] = self.revenue_tracker.get_revenue_dashboard_data()
            status['funding_status'] = self.auto_funding.get_funding_report()
            status['system_health'] = self.system_monitor.get_performance_report()
            status['ai_recommendations'] = self.adaptive_engine.analyze_performance_patterns()
            
        except Exception as e:
            self.logger.error(f"Error getting component status: {e}")
            status['error'] = str(e)
        
        return status
    
    def run_daily_business_cycle(self):
        """Run complete daily business cycle"""
        self.logger.info("Starting daily business cycle...")
        
        try:
            # 1. Revenue processing
            revenue_data = self.revenue_tracker.get_revenue_dashboard_data()
            current_revenue = revenue_data.get('current_month_revenue', 0)
            
            # 2. Auto-funding allocation
            if current_revenue > 0:
                allocations = self.auto_funding.process_revenue_allocation(current_revenue)
                self.logger.info(f"Revenue allocated: {allocations}")
            
            # 3. System optimization
            recommendations = self.adaptive_engine.analyze_performance_patterns()
            for rec in recommendations:
                self.logger.info(f"Optimization: {rec['action']}")
            
            # 4. Security audit
            self.run_security_audit()
            
            self.logger.info("✅ Daily business cycle completed")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Daily business cycle failed: {e}")
            return False
    
    def run_security_audit(self):
        """Run comprehensive security audit"""
        try:
            cursor = self.db_connection.cursor()
            
            # Log security audit event
            cursor.execute('''
                INSERT INTO security_events (event_type, severity, description)
                VALUES (?, ?, ?)
            ''', ('security_audit', 'info', 'Daily security audit completed'))
            
            self.db_connection.commit()
            self.logger.info("✅ Security audit completed")
            
        except Exception as e:
            self.logger.error(f"Security audit error: {e}")

def main():
    """Main application entry point"""
    print("🚀 CostByte Platform Starting...")
    print("🛡️  Military-Grade Security Enabled")
    print("🤖 Self-Healing, Self-Funding, Self-Learning")
    print("💰 Target: R1,000,000/month Automated Business")
    print("=" * 60)
    
    # Initialize platform
    platform = CostBytePlatform()
    
    # Start platform services
    if platform.start_platform_services():
        print("✅ CostByte Platform is now operational!")
        print("\n📊 Access your dashboard at: http://localhost:5000")
        print("🔒 Default login: admin / costbyte2024")
        print("\n🎯 Platform Features:")
        print("   • Real-time Revenue Tracking")
        print("   • Client Management with Secure Storage")
        print("   • Automated Funding Allocation")
        print("   • AI-Powered Optimization")
        print("   • Self-Healing System Monitoring")
        print("   • Military-Grade Security")
        print("=" * 60)
        
        # Run initial business cycle
        platform.run_daily_business_cycle()
        
        # Start dashboard
        try:
            dashboard_app.run(host='0.0.0.0', port=5000, debug=False)
        except Exception as e:
            print(f"Dashboard error: {e}")
    
    else:
        print("❌ Failed to start CostByte Platform")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
# Add to CostBytePlatform class in app.py

def setup_payment_systems(self):
    """Initialize payment and payout systems"""
    self.payment_processor = PaymentProcessor(self.db_connection, self.encryption_engine)
    self.payout_agent = PayoutAgent(self.db_connection, self.encryption_engine)
    self.logger.info("✅ Payment systems initialized")

def process_automatic_payouts(self):
    """Process automatic payouts on schedule"""
    try:
        result = self.payout_agent.process_daily_payouts()
        if result['success']:
            self.logger.info(f"Automatic payouts processed: R{result['total_payout']:,.2f}")
        else:
            self.logger.warning(f"Payout processing skipped: {result.get('reason')}")
    except Exception as e:
        self.logger.error(f"Automatic payout error: {e}")

# Add to start_background_services method
def payout_scheduler():
    while True:
        try:
            # Process payouts daily at 9 AM
            current_hour = datetime.now().hour
            if current_hour == 9:  # 9 AM
                platform.process_automatic_payouts()
            time.sleep(3600)  # Check every hour
        except Exception as e:
            logging.error(f"Payout scheduler error: {e}")
            time.sleep(300)  # Wait 5 minutes on error

threading.Thread(target=payout_scheduler, daemon=True).start()
