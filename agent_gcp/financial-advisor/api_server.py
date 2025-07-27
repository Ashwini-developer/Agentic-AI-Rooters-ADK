import sys
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn
import asyncio
from datetime import datetime

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Add the financial_advisor directory to Python path
financial_advisor_dir = os.path.join(current_dir, 'financial_advisor')
if financial_advisor_dir not in sys.path:
    sys.path.insert(0, financial_advisor_dir)

try:
    from financial_advisor.integrated_fomc_financial_agent import run_integrated_agent, get_integration_status
    from financial_advisor.agent import is_valid_phone_number
    AGENTS_AVAILABLE = True
    print("✅ Financial Advisor agents loaded successfully")
except ImportError as e:
    print(f"⚠️  Import error: {e}")
    print("🔄 Creating mock implementations...")
    AGENTS_AVAILABLE = False
    
    def run_integrated_agent(phone_number, otp, fomc_input, financial_input):
        if phone_number != "1010101010" or otp != "123456":
            return {"error": "Invalid credentials"}
        
        return f"""
# 🏦 Mock Integrated Financial Analysis

## 📋 FOMC Research Analysis
**Query:** {fomc_input}

**Key Findings:**
- Current interest rate policy remains data-dependent
- Inflation trends are being closely monitored
- Economic indicators suggest cautious optimism
- Future policy decisions will be based on incoming economic data

## 💰 Financial Advisory Recommendations
**Query:** {financial_input}

**Personalized Advice:**
- Consider maintaining a diversified portfolio approach
- Monitor interest rate changes for bond allocation adjustments  
- Review your risk tolerance in light of current monetary policy
- Dollar-cost averaging may be beneficial in current market conditions

## 🔗 Integrated Insights
The current monetary policy environment suggests a measured approach to investment decisions. Given the data-dependent nature of policy decisions, maintaining flexibility in your investment strategy is recommended.

**⚠️ Note:** This is a mock response for testing purposes. Real agents are not currently available.
        """
    
    def get_integration_status():
        return {
            "fomc_available": False,
            "financial_available": False,
            "integration_mode": "mock",
            "mock_components": ["fomc", "financial"]
        }
    
    def is_valid_phone_number(phone):
        return len(str(phone)) == 10 and str(phone).isdigit()

# Initialize FastAPI app
app = FastAPI(
    title="Financial Advisor Agent API",
    description="API for financial analysis and trading recommendations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request validation
class AuthRequest(BaseModel):
    phone_number: str
    otp: str

class TradingAnalysisRequest(BaseModel):
    phone_number: str
    otp: str
    query: str

class IntegratedAnalysisRequest(BaseModel):
    phone_number: str
    otp: str
    mpc_prompt: str
    fin_prompt: str

class UserData(BaseModel):
    phone_number: str
    name: str
    available: bool

# Test users data
TEST_USERS = [
    {"phone_number": "1010101010", "name": "Test User 1", "available": True},
    {"phone_number": "2020202020", "name": "Test User 2", "available": True},
    {"phone_number": "3030303030", "name": "Test User 3", "available": True},
]

@app.get("/")
async def root():
    try:
        integration_status = get_integration_status()
    except:
        integration_status = {"error": "Status unavailable"}
    
    return {
        "message": "Financial Advisor Agent API",
        "version": "1.0.0",
        "agents_available": AGENTS_AVAILABLE,
        "integration_status": integration_status,
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "authenticate": "/authenticate",
            "trading_analysis": "/trading_analysis", 
            "integrated_analysis": "/integrated_analysis",
            "users": "/users"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/status")
async def integration_status():
    """Get the current integration status of all agents"""
    try:
        status = get_integration_status()
        return {
            "api_status": "healthy",
            "agents_available": AGENTS_AVAILABLE,
            "integration_status": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "api_status": "healthy",
            "agents_available": False,
            "integration_status": {
                "fomc_available": False,
                "financial_available": False,
                "integration_mode": "error",
                "error": str(e)
            },
            "timestamp": datetime.now().isoformat()
        }

@app.post("/authenticate")
async def authenticate(request: AuthRequest):
    """Authenticate user with phone number and OTP"""
    try:
        if not is_valid_phone_number(request.phone_number):
            raise HTTPException(status_code=400, detail="Invalid phone number format")
        
        if request.otp != "123456":  # Demo OTP
            raise HTTPException(status_code=401, detail="Invalid OTP")
        
        return {
            "authenticated": True,
            "phone_number": request.phone_number,
            "message": "Authentication successful"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication error: {str(e)}")

@app.post("/trading_analysis")
async def trading_analysis(request: TradingAnalysisRequest):
    """Get trading analysis and recommendations"""
    try:
        # Authenticate first
        if not is_valid_phone_number(request.phone_number):
            raise HTTPException(status_code=400, detail="Invalid phone number")
        
        if request.otp != "123456":
            raise HTTPException(status_code=401, detail="Invalid OTP")
        
        # For now, return a structured response until the trading agent is properly integrated
        result = {
            "analysis_type": "trading",
            "query": request.query,
            "recommendations": f"Trading analysis for: {request.query}",
            "risk_assessment": "Moderate risk based on current market conditions",
            "suggested_allocation": "Consider diversified portfolio approach",
            "timestamp": datetime.now().isoformat()
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")

@app.post("/integrated_analysis")
async def integrated_analysis(request: IntegratedAnalysisRequest):
    """Get integrated FOMC research and financial analysis"""
    try:
        print(f"🔄 Processing integrated analysis request for user: {request.phone_number}")
        
        result = run_integrated_agent(
            phone_number=request.phone_number,
            otp=request.otp,
            fomc_input=request.mpc_prompt,
            financial_input=request.fin_prompt
        )
        
        if isinstance(result, dict) and "error" in result:
            print(f"❌ Analysis error: {result['error']}")
            raise HTTPException(status_code=400, detail=result["error"])
        
        print("✅ Integrated analysis completed successfully")
        
        return {
            "success": True,
            "analysis_type": "integrated",
            "result": result,
            "agents_available": AGENTS_AVAILABLE,
            "mpc_prompt": request.mpc_prompt,
            "financial_prompt": request.fin_prompt,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Integrated analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Integrated analysis error: {str(e)}")

@app.get("/users")
async def get_test_users():
    """Get list of available test users"""
    return {"test_users": TEST_USERS}

if __name__ == "__main__":
    print("🏦 Starting Financial Advisor Agent API...")
    print("📊 API will be available at: http://localhost:8000")
    print("📚 API documentation at: http://localhost:8000/docs")
    print("🔧 Integration status at: http://localhost:8000/status")
    
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )