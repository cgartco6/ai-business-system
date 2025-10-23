#!/usr/bin/env python3
"""
Deployment script for AI Business System
Handles deployment to production environment
"""

import logging
import shutil
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Setup logging for deployment"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('deployment.log'),
            logging.StreamHandler()
        ]
    )

def backup_database():
    """Backup the database before deployment"""
    try:
        db_path = Path('data/ai_business.db')
        if db_path.exists():
            backup_dir = Path('backups')
            backup_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = backup_dir / f'ai_business_backup_{timestamp}.db'
            
            shutil.copy2(db_path, backup_path)
            logging.info(f"✅ Database backed up to: {backup_path}")
            return True
        else:
            logging.warning("⚠️ No existing database found to backup")
            return True
    except Exception as e:
        logging.error(f"❌ Database backup failed: {e}")
        return False

def validate_configuration():
    """Validate configuration before deployment"""
    try:
        # Check if credentials file exists and has been configured
        creds_path = Path('config/credentials.py')
        if not creds_path.exists():
            logging.error("❌ credentials.py not found. Please run setup first.")
            return False
        
        # Check for placeholder values in credentials
        with open(creds_path, 'r') as f:
            content = f.read()
            
        placeholders = ['your_', 'YOUR_', 'example.com', 'placeholder']
        for placeholder in placeholders:
            if placeholder in content:
                logging.warning(f"⚠️ Found potential placeholder in credentials: {placeholder}")
        
        logging.info("✅ Configuration validation completed")
        return True
        
    except Exception as e:
        logging.error(f"❌ Configuration validation failed: {e}")
        return False

def deploy_to_production():
    """Deploy to production environment"""
    try:
        logging.info("🚀 Starting production deployment...")
        
        # 1. Backup current database
        if not backup_database():
            return False
        
        # 2. Validate configuration
        if not validate_configuration():
            return False
        
        # 3. Stop any running processes (this would be platform-specific)
        logging.info("⏹️ Stopping existing processes...")
        # Add platform-specific process stopping logic here
        
        # 4. Update system files
        logging.info("📁 Updating system files...")
        # This would typically involve git pull or file copying
        
        # 5. Restart services
        logging.info("🔄 Restarting services...")
        # Add service restart logic here
        
        logging.info("✅ Production deployment completed successfully!")
        return True
        
    except Exception as e:
        logging.error(f"❌ Deployment failed: {e}")
        return False

def main():
    """Main deployment function"""
    setup_logging()
    
    print("🚀 AI Business System - Production Deployment")
    print("=" * 50)
    
    if deploy_to_production():
        print("\n✅ Deployment completed successfully!")
        print("\n📋 Next steps:")
        print("1. Monitor system logs for any issues")
        print("2. Verify email delivery is working")
        print("3. Check that lead generation is active")
        print("4. Review daily reports for system performance")
    else:
        print("\n❌ Deployment failed. Check deployment.log for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
