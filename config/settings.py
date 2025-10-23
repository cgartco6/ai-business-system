import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Afrihost Database Configuration
DATABASE_CONFIG = {
    'host': 'localhost',  # Update with Afrihost DB host
    'port': 3306,
    'user': 'your_username',
    'password': 'your_password',
    'database': 'ai_business_db',
    'charset': 'utf8mb4'
}

# Email Configuration (Afrihost)
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
    'linkedin': 'your_linkedin_api_key'
}

# Business Settings
BUSINESS_CONFIG = {
    'target_revenue': 1000000,  # 1M ZAR
    'service_price': 25000,     # Per client per month
    'target_clients': 40,
    'niche': 'SME Digital Marketing South Africa'
}
