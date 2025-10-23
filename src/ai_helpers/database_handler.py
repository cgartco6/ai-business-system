import mysql.connector
import sqlite3
import logging
from pathlib import Path

class DatabaseHandler:
    def __init__(self, config, use_sqlite=False):
        self.config = config
        self.use_sqlite = use_sqlite
        self.connection = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Connect to database"""
        try:
            if self.use_sqlite:
                # For local development
                db_path = Path(__file__).parent.parent.parent / 'data' / 'business.db'
                db_path.parent.mkdir(parents=True, exist_ok=True)
                self.connection = sqlite3.connect(db_path)
                self.logger.info("Connected to SQLite database")
            else:
                # For production (Afrihost MySQL)
                self.connection = mysql.connector.connect(**self.config)
                self.logger.info("Connected to MySQL database")
            
            self._initialize_tables()
            return True
            
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False
    
    def _initialize_tables(self):
        """Initialize database tables"""
        cursor = self.connection.cursor()
        
        # Leads table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                company_name VARCHAR(255) NOT NULL,
                contact_email VARCHAR(255),
                industry VARCHAR(100),
                size VARCHAR(50),
                lead_score INTEGER DEFAULT 0,
                status VARCHAR(50) DEFAULT 'new',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Outreach log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outreach_log (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                lead_id INTEGER,
                campaign_type VARCHAR(100),
                status VARCHAR(50),
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Clients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                company_name VARCHAR(255) NOT NULL,
                contact_person VARCHAR(255),
                email VARCHAR(255),
                monthly_rate DECIMAL(10,2),
                start_date DATE,
                status VARCHAR(50) DEFAULT 'active'
            )
        ''')
        
        self.connection.commit()
