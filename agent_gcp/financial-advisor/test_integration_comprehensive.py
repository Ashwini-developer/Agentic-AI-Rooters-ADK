#!/usr/bin/env python3
"""
Test script for the integrated FOMC + Financial Advisor system
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'financial_advisor'))

def test_direct_integration():
    """Test the integration function directly"""
    print("🧪 Testing Direct Integration")
    print("=" * 50)
    
    try:
        from financial_advisor.integrated_fomc_financial_agent import run_integrated_agent, get_integration_status
        
        # Check integration status
        status = get_integration_status()
        print(f"📊 Integration Status: {json.dumps(status, indent=2)}")
        
        # Test the integration
        result = run_integrated_agent(
            phone_number="1010101010",
            otp="123456",
            fomc_input="Analyze the latest Federal Reserve policy decisions and their impact on markets.",
            financial_input="Based on current monetary policy, what investment strategies should I consider for my portfolio?"
        )
        
        print(f"\n✅ Integration Result:")
        print("-" * 40)
        if isinstance(result, dict):
            print(json.dumps(result, indent=2))
        else:
            print(result)
        
    except Exception as e:
        print(f"❌ Direct integration test failed: {e}")
        import traceback
        traceback.print_exc()

def test_api_integration():
    """Test the integration via API"""
    print("\n🌐 Testing API Integration")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    try:
        # Test API health
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print("❌ API server is not responding correctly")
            return
        
        # Test integration status
        response = requests.get(f"{base_url}/status", timeout=5)
        if response.status_code == 200:
            print(f"📊 API Integration Status: {json.dumps(response.json(), indent=2)}")
        
        # Test integrated analysis
        data = {
            "phone_number": "1010101010",
            "otp": "123456",
            "mpc_prompt": "What are the key takeaways from the latest FOMC meeting?",
            "fin_prompt": "How should I adjust my investment strategy based on current monetary policy?"
        }
        
        response = requests.post(f"{base_url}/integrated_analysis", json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ API Integration Result:")
            print("-" * 40)
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Error: {response.text}")
    
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server. Please start the server first:")
        print("   python api_server.py")
    except Exception as e:
        print(f"❌ API integration test failed: {e}")

def main():
    """Main test function"""
    print("🏦 Financial Advisor Integration Test Suite")
    print("=" * 60)
    print(f"⏰ Test started at: {datetime.now()}")
    
    # Test 1: Direct integration
    test_direct_integration()
    
    # Test 2: API integration
    test_api_integration()
    
    print("\n🎯 Test Summary:")
    print("- Direct integration test checks if the agents can be imported and run")
    print("- API integration test checks if the FastAPI server is working")
    print("- Both tests use mock agents if real agents are not available")
    print("\n✅ Integration testing completed!")

if __name__ == "__main__":
    main()
