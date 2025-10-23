# CostByte API Configuration - Encrypted
ENCRYPTED_CONFIG = {
    # Bank API Configuration (Encrypted)
    'bank_api': 'gAAAAABl7V2a...encrypted...',
    'bank_secret': 'gAAAAABl7V2a...encrypted...',
    
    # Payment Gateway (Encrypted)
    'payfast_merchant_id': 'gAAAAABl7V2a...encrypted...',
    'payfast_merchant_key': 'gAAAAABl7V2a...encrypted...',
    
    # Email Service (Encrypted)
    'smtp_credentials': 'gAAAAABl7V2a...encrypted...',
    
    # External APIs (Encrypted)
    'openai_api_key': 'gAAAAABl7V2a...encrypted...',
    'google_api_key': 'gAAAAABl7V2a...encrypted...',
    'linkedin_api_key': 'gAAAAABl7V2a...encrypted...'
}

# Public Configuration
BUSINESS_CONFIG = {
    'company_name': 'CostByte',
    'target_revenue': 1000000,  # 1M ZAR per month
    'service_tiers': {
        'basic': 15000,
        'professional': 25000,
        'enterprise': 50000
    },
    'auto_funding_rules': {
        'platform_maintenance': 0.10,  # 10% of revenue
        'owner_compensation': 0.30,    # 30% of revenue
        'reinvestment': 0.40,          # 40% for growth
        'tax_reserve': 0.20            # 20% for taxes
    }
}
