#!/usr/bin/env python3
"""
Setup script for the Neo4j MCP server.
"""

import subprocess
import sys
import os
from dotenv import load_dotenv

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("Setting up Neo4j MCP Server...")
    print("=" * 50)
    
    # Check if Python 3.8+ is available
    if sys.version_info < (3, 8):
        print("✗ Python 3.8 or higher is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing dependencies"):
        print("\nFailed to install dependencies. Please check your Python environment.")
        sys.exit(1)
    
    # Make scripts executable
    scripts = ["server.py", "test_comprehensive.py"]
    for script in scripts:
        if os.path.exists(script):
            run_command(f"chmod +x {script}", f"Making {script} executable")
            
    # Load environment variables
    load_dotenv()        
    
    print("\n" + "=" * 50)
    print("✓ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Start a Neo4j instance (if you have one)")
    print("2. Run the server: python server.py")
    print("3. Or test with Neo4j: python test_comprehensive.py")
    print("\nFor more information, see README.md")

if __name__ == "__main__":
    main() 