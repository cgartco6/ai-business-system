#!/usr/bin/env python3
"""
Backup script for AI Business System
Automates database and configuration backups
"""

import shutil
import json
from datetime import datetime
from pathlib import Path
import logging

def setup_backup_logging():
    """Setup logging for backup operations"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('backup_operations.log'),
            logging.StreamHandler()
        ]
    )

def create_backup():
    """Create a comprehensive backup of the system"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = Path('backups') / f'backup_{timestamp}'
    
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"📁 Creating backup in: {backup_dir}")
        
        # 1. Backup database
        db_path = Path('data/ai_business.db')
        if db_path.exists():
            shutil.copy2(db_path, backup_dir / 'ai_business.db')
            logging.info("✅ Database backed up")
        else:
            logging.warning("⚠️ Database file not found")
        
        # 2. Backup configuration
        config_files = ['config/settings.py', 'config/credentials.py']
        config_backup_dir = backup_dir / 'config'
        config_backup_dir.mkdir(exist_ok=True)
        
        for config_file in config_files:
            config_path = Path(config_file)
            if config_path.exists():
                shutil.copy2(config_path, config_backup_dir / config_path.name)
                logging.info(f"✅ {config_file} backed up")
        
        # 3. Backup recent reports
        reports_dir = Path('data/reports')
        if reports_dir.exists():
            reports_backup_dir = backup_dir / 'reports'
            shutil.copytree(reports_dir, reports_backup_dir, dirs_exist_ok=True)
            logging.info("✅ Reports backed up")
        
        # 4. Create backup manifest
        manifest = {
            'backup_timestamp': timestamp,
            'backup_date': datetime.now().isoformat(),
            'components_backed_up': ['database', 'configuration', 'reports'],
            'backup_size': get_directory_size(backup_dir),
            'system_version': '1.0.0'
        }
        
        with open(backup_dir / 'backup_manifest.json', 'w') as f:
            json.dump(manifest, f, indent=2)
        
        logging.info(f"✅ Backup completed successfully: {backup_dir}")
        return backup_dir
        
    except Exception as e:
        logging.error(f"❌ Backup failed: {e}")
        return None

def get_directory_size(path):
    """Calculate directory size in MB"""
    total_size = 0
    for file_path in Path(path).rglob('*'):
        if file_path.is_file():
            total_size += file_path.stat().st_size
    return f"{total_size / (1024 * 1024):.2f} MB"

def cleanup_old_backups(max_backups=10):
    """Clean up old backups, keeping only the most recent ones"""
    try:
        backups_dir = Path('backups')
        if not backups_dir.exists():
            return
        
        backups = sorted(backups_dir.glob('backup_*'), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if len(backups) > max_backups:
            for old_backup in backups[max_backups:]:
                shutil.rmtree(old_backup)
                logging.info(f"🗑️ Removed old backup: {old_backup.name}")
        
        logging.info(f"✅ Cleaned up old backups, keeping {min(len(backups), max_backups)}")
        
    except Exception as e:
        logging.error(f"❌ Backup cleanup failed: {e}")

def main():
    """Main backup function"""
    setup_backup_logging()
    
    print("💾 AI Business System - Backup Utility")
    print("=" * 50)
    
    # Create new backup
    backup_path = create_backup()
    
    if backup_path:
        print(f"✅ Backup created successfully: {backup_path}")
        
        # Clean up old backups
        cleanup_old_backups()
        
        print("\n📊 Backup summary:")
        print(f"   Location: {backup_path}")
        print(f"   Size: {get_directory_size(backup_path)}")
        print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    else:
        print("❌ Backup failed")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
