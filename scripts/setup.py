#!/usr/bin/env python3
"""
Setup script for AI Business System
Run this first to initialize the system
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command):
    """Run system command and handle errors"""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running command: {command}")
        print(f"Error: {e}")
        return False

def main():
    print("🚀 Setting up AI Business System...")
    print("💻 Optimized for Windows 10 i7 16GB RAM")
    print("🌍 South Africa Market Focus")
    print("🎯 Target: R1,000,000/month")
    print("=" * 60)
    
    # Create necessary directories
    directories = ['data', 'logs', 'data/reports', 'data/exports']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"📁 Created directory: {directory}")
    
    # Install requirements
    print("\n📦 Installing dependencies...")
    if not run_command(f'"{sys.executable}" -m pip install -r requirements.txt'):
        print("❌ Failed to install dependencies")
        return False
    
    # Initialize database
    print("\n🗄️ Initializing database...")
    try:
        # Add the src directory to Python path
        sys.path.append(str(Path(__file__).parent.parent / 'src'))
        
        from main import AIBusinessOrchestrator
        orchestrator = AIBusinessOrchestrator()
        if orchestrator.setup():
            print("✅ Database initialized successfully!")
        else:
            print("❌ Database initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        return False
    
    # Create credentials template if it doesn't exist
    creds_template = Path('config/credentials_template.py')
    if not creds_template.exists():
        print("❌ credentials_template.py not found - please check the config directory")
        return False
    
    # Copy credentials template
    creds_file = Path('config/credentials.py')
    if not creds_file.exists():
        import shutil
        shutil.copy2(creds_template, creds_file)
        print("📝 Created credentials.py from template")
        print("   Please edit config/credentials.py with your actual API keys and credentials")
    
    print("\n" + "=" * 60)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Edit config/credentials.py with your actual API keys and database credentials")
    print("2. Run 'python main.py' to start the system")
    print("3. Check logs/ai_business.log for detailed operation logs")
    print("4. Monitor data/reports/ for daily performance reports")
    print("\n🎯 Your system is ready to start generating R1,000,000/month!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
