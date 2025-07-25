"""
Script to Start Development Environment

This script helps developers quickly set up and start the development environment
for the Data Protection AI Assistant.

Author: Adryan R A
"""

import os
import sys
import subprocess
import time
from pathlib import Path


def check_requirements():
    """Check if all requirements are installed."""
    print("Checking requirements...")
    
    try:
        import docker
        print("Docker Python client available")
    except ImportError:
        print("Docker Python client not found. Install with: pip install docker")
        return False
    
    # Check if Docker is running
    try:
        client = docker.from_env()
        client.ping()
        print("Docker daemon is running")
    except Exception:
        print("Docker daemon is not running. Please start Docker.")
        return False
    
    return True


def setup_environment():
    """Set up the development environment."""
    print("Setting up environment...")
    
    # Create .env from template if it doesn't exist
    env_file = Path(".env")
    env_template = Path(".env.template")
    
    if not env_file.exists() and env_template.exists():
        print("Creating .env file from template...")
        env_file.write_text(env_template.read_text())
        print("Please edit .env file with your API keys before proceeding!")
        return False
    elif not env_file.exists():
        print("No .env file found. Please create one with your configuration.")
        return False
    
    # Create necessary directories
    dirs_to_create = ["logs", "data/gdpr", "data/uupdp", "data/company"]
    for dir_path in dirs_to_create:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    return True


def start_services():
    """Start the development services."""
    print("Starting services...")
    
    # Start with docker-compose
    try:
        subprocess.run(["docker-compose", "up", "-d", "elasticsearch"], check=True)
        print("Elasticsearch started")
        
        # Wait for Elasticsearch to be ready
        print("Waiting for Elasticsearch to be ready...")
        time.sleep(30)
        
        # Install Python dependencies
        print("Installing Python dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        
        # Start the application
        print("Starting Data Protection AI Assistant...")
        subprocess.run([sys.executable, "main.py", "--both", "--debug"])
        
    except subprocess.CalledProcessError as e:
        print(f"Error starting services: {e}")
        return False
    except KeyboardInterrupt:
        print("\nStopping services...")
        subprocess.run(["docker-compose", "down"])
        return False
    
    return True


def main():
    """Main development setup function."""
    print("Data Protection AI Assistant - Development Setup")
    print("Author: Adryan R A")
    print("=" * 60)
    
    if not check_requirements():
        sys.exit(1)
    
    if not setup_environment():
        print("\nNext steps:")
        print("1. Edit .env file with your API keys")
        print("2. Run this script again")
        sys.exit(1)
    
    if not start_services():
        sys.exit(1)
    
    print("Development environment is ready!")
    print("\nAccess points:")
    print("- API Documentation: http://localhost:8000/docs")
    print("- Web Interface: http://localhost:7860")
    print("- Elasticsearch: http://localhost:9200")


if __name__ == "__main__":
    main()
