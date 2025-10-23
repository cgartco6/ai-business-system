import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

# Create directories
LOG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Database Configuration
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'ai_business_user',
    'password': 'your_password_here',
    'database': 'ai_business_db',
    'charset': 'utf8mb4'
}

# SQLite fallback for local development
SQLITE_PATH = DATA_DIR / "ai_business.db"

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': 'mail.afrihost.com',
    'smtp_port': 587,
    'username': 'your_email@yourdomain.co.za',
    'password': 'your_email_password',
    'use_tls': True
}

# API Keys (You'll need to obtain these)
API_KEYS = {
    'openai': 'your_openai_key_here',
    'google_trends': 'your_google_trends_key',
    'serpapi': 'your_serpapi_key_here'
}

# Business Settings
BUSINESS_CONFIG = {
    'target_revenue': 1000000,  # 1M ZAR
    'service_price': 25000,     # Per client per month
    'target_clients': 40,
    'niche': 'SME Digital Marketing South Africa',
    'company_name': 'AI Growth Solutions SA',
    'base_currency': 'ZAR'
}

# System Settings
SYSTEM_CONFIG = {
    'max_leads_per_day': 100,
    'max_emails_per_day': 200,
    'log_level': 'INFO',
    'backup_interval_hours': 24
}
