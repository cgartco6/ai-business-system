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
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        return False

def main():
    print("Setting up AI Business System...")
    
    # Create necessary directories
    directories = ['data', 'logs', 'reports', 'exports']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Install requirements
    print("Installing dependencies...")
    if not run_command(f'"{sys.executable}" -m pip install -r requirements.txt'):
        print("Failed to install dependencies")
        return False
    
    # Initialize database
    print("Initializing database...")
    try:
        from main import AIBusinessOrchestrator
        orchestrator = AIBusinessOrchestrator()
        if orchestrator.setup():
            print("✅ Setup completed successfully!")
            print("\nNext steps:")
            print("1. Update config/credentials.py with your actual API keys and database credentials")
            print("2. Run 'python main.py' to start the system")
            print("3. Check ai_business.log for detailed logs")
            return True
        else:
            print("❌ Setup failed")
            return False
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        return False

if __name__ == "__main__":
    main()
