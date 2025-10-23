import logging
import sqlite3
import mysql.connector
from pathlib import Path
from typing import Dict, List

class DatabaseHandler:
    def __init__(self, config: Dict, use_sqlite: bool = True):
        self.config = config
        self.use_sqlite = use_sqlite
        self.connection = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self) -> bool:
        """Connect to database"""
        try:
            if self.use_sqlite:
                # For local development
                db_path = Path(__file__).parent.parent.parent / 'data' / 'ai_business.db'
                db_path.parent.mkdir(parents=True, exist_ok=True)
                self.connection = sqlite3.connect(db_path)
                self.logger.info("Connected to SQLite database")
            else:
                # For production (MySQL)
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
                id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                contact_email TEXT,
                contact_name TEXT,
                industry TEXT,
                size TEXT,
                location TEXT,
                lead_score REAL DEFAULT 0,
                qualified_score REAL DEFAULT 0,
                status TEXT DEFAULT 'new',
                priority TEXT DEFAULT 'medium',
                source TEXT,
                last_contacted DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Outreach log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS outreach_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id TEXT,
                campaign_id TEXT,
                campaign_type TEXT,
                status TEXT,
                error_message TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads (id)
            )
        ''')
        
        # Clients table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT NOT NULL,
                contact_person TEXT,
                email TEXT,
                monthly_rate DECIMAL(10,2),
                start_date DATE,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Follow-up schedule table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS follow_up_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id TEXT,
                follow_up_type TEXT,
                scheduled_date DATETIME,
                subject TEXT,
                template TEXT,
                status TEXT DEFAULT 'scheduled',
                sent_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads (id)
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
        
        self.connection.commit()
        self.logger.info("Database tables initialized")
    
    def execute_query(self, query: str, params: tuple = None) -> List:
        """Execute a query and return results"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            else:
                self.connection.commit()
                return []
                
        except Exception as e:
            self.logger.error(f"Query execution error: {e}")
            return []
    
    def insert_lead(self, lead_data: Dict) -> bool:
        """Insert a new lead"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO leads 
                (id, company_name, contact_email, contact_name, industry, size, location, lead_score, status, priority, source)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                lead_data['id'], lead_data['company_name'], lead_data['contact_email'],
                lead_data.get('contact_name', ''), lead_data['industry'], lead_data['size'],
                lead_data['location'], lead_data['lead_score'], lead_data['status'],
                lead_data['priority'], lead_data['source']
            ))
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error inserting lead: {e}")
            return False
    
    def get_leads(self, status: str = None, priority: str = None, limit: int = 100) -> List[Dict]:
        """Get leads with optional filters"""
        try:
            query = "SELECT * FROM leads WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if priority:
                query += " AND priority = ?"
                params.append(priority)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting leads: {e}")
            return []
    
    def update_lead_status(self, lead_id: str, new_status: str) -> bool:
        """Update lead status"""
        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                UPDATE leads SET status = ?, last_contacted = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (new_status, lead_id))
            self.connection.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error updating lead status: {e}")
            return False
    
    def get_system_metrics(self, metric_type: str = None, days: int = 7) -> List[Dict]:
        """Get system metrics"""
        try:
            query = '''
                SELECT * FROM system_metrics 
                WHERE recorded_at >= datetime('now', ?)
            '''
            params = [f'-{days} days']
            
            if metric_type:
                query += " AND metric_type = ?"
                params.append(metric_type)
            
            query += " ORDER BY recorded_at DESC"
            
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            
            columns = [col[0] for col in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error getting metrics: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.logger.info("Database connection closed")
