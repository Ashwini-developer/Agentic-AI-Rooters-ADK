#!/usr/bin/env python3
"""
Comprehensive startup script for Financial Advisor + FOMC integration
"""

import os
import sys
import subprocess
import time
import threading
import signal
from pathlib import Path

def setup_environment():
    """Setup Python environment and paths"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    financial_advisor_dir = os.path.join(current_dir, 'financial_advisor')
    
    # Add to sys.path
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    if financial_advisor_dir not in sys.path:
        sys.path.insert(0, financial_advisor_dir)
    
    # Set environment variables
    os.environ['PYTHONPATH'] = os.pathsep.join([
        os.environ.get('PYTHONPATH', ''),
        current_dir,
        financial_advisor_dir
    ])
    
    print(f"✅ Environment setup complete")
    print(f"   Current dir: {current_dir}")
    print(f"   Financial advisor dir: {financial_advisor_dir}")

def check_integration():
    """Check if the integration is working"""
    print("🔍 Checking integration status...")
    
    try:
        # Setup environment first
        setup_environment()
        
        # Try to import and test the integration
        from financial_advisor.integrated_fomc_financial_agent import get_integration_status
        status = get_integration_status()
        
        print(f"📊 Integration Status:")
        print(f"   FOMC Available: {'✅' if status['fomc_available'] else '❌'}")
        print(f"   Financial Available: {'✅' if status['financial_available'] else '❌'}")
        print(f"   Mode: {status['integration_mode']}")
        
        if status['mock_components']:
            print(f"   Mock Components: {', '.join(status['mock_components'])}")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Integration check failed: {e}")
        print("🔄 The system will run in mock mode")
        return False

def run_fastapi_server():
    """Run the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    try:
        # Change to the script directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Run the server
        subprocess.run([
            sys.executable, "api_server.py"
        ])
    except KeyboardInterrupt:
        print("\n🛑 FastAPI server stopped")
    except Exception as e:
        print(f"❌ FastAPI server error: {e}")

def run_streamlit_app():
    """Run the Streamlit app"""
    print("🌐 Starting Streamlit frontend...")
    
    # Wait for FastAPI to start
    time.sleep(3)
    
    try:
        # Check if FastAPI is running
        import requests
        try:
            response = requests.get("http://localhost:8000/dev-ui/", timeout=5)
            if response.status_code == 200:
                print("✅ FastAPI server confirmed running")
            else:
                print("⚠️  FastAPI server not responding correctly")
        except:
            print("⚠️  Cannot connect to FastAPI server")
        
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_frontend.py",
            "--server.port", "8501",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Streamlit app stopped")
    except Exception as e:
        print(f"❌ Streamlit app error: {e}")

def main():
    """Main startup function"""
    print("🏦 Financial Advisor + FOMC Integration Startup")
    print("=" * 60)
    
    # Check integration
    integration_ok = check_integration()
    
    print("\n🚀 Starting services...")
    print("📌 FastAPI will run on: http://localhost:8000")
    print("📌 Streamlit will run on: http://localhost:8501")
    print("📌 Press Ctrl+C to stop all services")
    print("=" * 60)
    
    try:
        # Start FastAPI in background thread
        fastapi_thread = threading.Thread(target=run_fastapi_server, daemon=True)
        fastapi_thread.start()
        
        # Start Streamlit in main thread
        run_streamlit_app()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down all services...")
        print("✅ Shutdown complete")

if __name__ == "__main__":
    main()
