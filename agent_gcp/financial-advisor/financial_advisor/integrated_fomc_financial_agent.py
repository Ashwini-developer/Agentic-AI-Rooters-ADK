import os
import json
import logging
import traceback

# Setup logging
logger = logging.getLogger(__name__)

# Try to import the FOMC research agent
try:
    from .fomc_research.agent import root_agent as fomc_root_agent
    FOMC_AVAILABLE = True
    logger.info("✅ FOMC research agent loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️  FOMC research agent not available: {e}")
    FOMC_AVAILABLE = False
    
    # Create a mock FOMC agent for fallback
    class MockFOMCAgent:
        def run(self, input_text, state=None):
            return {
                "output": f"Mock FOMC Research Analysis:\n\nQuery: {input_text}\n\nKey Findings:\n- Interest rate outlook remains data-dependent\n- Inflation trends continue to be monitored closely\n- Economic indicators suggest cautious optimism\n- Policy decisions will be based on incoming data\n\nNote: This is a mock response as the full FOMC research agent is not available.",
                "analysis_summary": "Mock monetary policy analysis",
                "key_insights": ["Data-dependent policy", "Inflation monitoring", "Cautious outlook"]
            }
    
    fomc_root_agent = MockFOMCAgent()

# Import the financial advisor agent
try:
    from .agent import root_agent as financial_root_agent, is_valid_phone_number
    FINANCIAL_AVAILABLE = True
    logger.info("✅ Financial advisor agent loaded successfully")
except ImportError as e:
    logger.error(f"❌ Financial advisor agent not available: {e}")
    FINANCIAL_AVAILABLE = False
    
    # Create a mock financial agent for fallback
    class MockFinancialAgent:
        def run(self, input_text, state=None):
            return {
                "output": f"Mock Financial Advisory Analysis:\n\nQuery: {input_text}\n\nRecommendations:\n- Maintain diversified portfolio\n- Consider current market conditions\n- Review risk tolerance\n- Monitor economic indicators\n\nNote: This is a mock response as the full financial advisor agent is not available."
            }
    
    financial_root_agent = MockFinancialAgent()
    
    def is_valid_phone_number(phone_number):
        """Mock phone validation - accepts 10-digit numbers"""
        return isinstance(phone_number, str) and phone_number.isdigit() and len(phone_number) == 10

def run_integrated_agent(phone_number, otp, fomc_input, financial_input):
    """
    Run integrated FOMC research and financial advisor analysis
    
    Args:
        phone_number (str): User's phone number for authentication
        otp (str): One-time password for authentication
        fomc_input (str): Query for FOMC research agent
        financial_input (str): Query for financial advisor agent
    
    Returns:
        dict or str: Combined analysis result or error message
    """
    logger.info(f"🔄 Starting integrated analysis for user: {phone_number}")
    
    # Step 1: Validate phone number
    if not is_valid_phone_number(phone_number):
        logger.warning(f"❌ Invalid phone number: {phone_number}")
        return {"error": "Invalid phone number."}
    
    # Step 2: Validate OTP (static for demo)
    if otp != "123456":
        logger.warning(f"❌ Invalid OTP for user: {phone_number}")
        return {"error": "Invalid OTP."}
    
    try:
        # Step 3: Load user data
        logger.info(f"📁 Loading user data for: {phone_number}")
        test_data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'test_data_dir')
        user_dir = os.path.join(test_data_dir, phone_number)
        user_data = {}
        
        if os.path.exists(user_dir):
            for fname in os.listdir(user_dir):
                if fname.endswith('.json'):
                    fpath = os.path.join(user_dir, fname)
                    try:
                        with open(fpath, 'r', encoding='utf-8') as f:
                            key = fname.replace('.json', '')
                            user_data[key] = json.load(f)
                        logger.debug(f"✅ Loaded {key} data")
                    except Exception as e:
                        logger.warning(f"⚠️  Failed to load {fname}: {e}")
                        user_data[key] = None
        else:
            logger.warning(f"⚠️  User directory not found: {user_dir}")
        
        # Step 4: Run FOMC research agent
        logger.info(f"🏛️ Running FOMC research agent...")
        fomc_state = {}
        
        try:
            fomc_result = fomc_root_agent.run(fomc_input, state=fomc_state)
            logger.info("✅ FOMC research completed successfully")
        except Exception as e:
            logger.error(f"❌ FOMC research failed: {e}")
            fomc_result = {
                "output": f"FOMC research encountered an error: {str(e)}",
                "error": True
            }
        
        # Extract FOMC output and state data
        fomc_output = ""
        if isinstance(fomc_result, dict):
            fomc_output = fomc_result.get('output', str(fomc_result))
        else:
            fomc_output = str(fomc_result)
        
        # Step 5: Prepare comprehensive state for financial agent
        logger.info(f"💼 Preparing financial agent context...")
        financial_state = {
            'phone_number': phone_number,
            'otp': otp,
            'user_data': user_data,
            'mpc_research_output': fomc_output,
            'fomc_available': FOMC_AVAILABLE,
            'financial_available': FINANCIAL_AVAILABLE,
            # FOMC state data
            'geopolitical_news': fomc_state.get('geopolitical_news', ''),
            'macroeconomic_news': fomc_state.get('macroeconomic_news', ''),
            'microeconomic_news': fomc_state.get('microeconomic_news', ''),
            'flight_log_details': fomc_state.get('flight_log_details', ''),
            'local_political_news': fomc_state.get('local_political_news', ''),
        }
        
        # Step 6: Run financial advisor agent
        logger.info(f"💰 Running financial advisor agent...")
        try:
            financial_result = financial_root_agent.run(financial_input, state=financial_state)
            logger.info("✅ Financial analysis completed successfully")
        except Exception as e:
            logger.error(f"❌ Financial analysis failed: {e}")
            financial_result = {
                "output": f"Financial analysis encountered an error: {str(e)}",
                "error": True
            }
        
        # Step 7: Format and return results
        if isinstance(financial_result, dict):
            final_result = financial_result.get('output', financial_result)
        else:
            final_result = str(financial_result)
        
        # Add integration metadata
        integration_info = f"""
        
📊 **Integration Status:**
- FOMC Research Agent: {'✅ Active' if FOMC_AVAILABLE else '⚠️ Mock Mode'}
- Financial Advisor Agent: {'✅ Active' if FINANCIAL_AVAILABLE else '⚠️ Mock Mode'}
- User Data Loaded: {'✅ Yes' if user_data else '❌ No'}
- Analysis Timestamp: {json.dumps(user_data.keys()) if user_data else 'N/A'}

🔗 **Integration Flow:**
1. FOMC Query: "{fomc_input}"
2. Financial Query: "{financial_input}"
3. Combined Analysis: Monetary policy insights integrated with personalized financial advice
        """
        
        if isinstance(final_result, str):
            final_result += integration_info
        
        logger.info("✅ Integrated analysis completed successfully")
        return final_result
            
    except Exception as e:
        error_msg = f"An error occurred during integrated analysis: {str(e)}"
        logger.error(f"❌ {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": error_msg}

def get_integration_status():
    """Get the current status of the integration"""
    return {
        "fomc_available": FOMC_AVAILABLE,
        "financial_available": FINANCIAL_AVAILABLE,
        "integration_mode": "full" if (FOMC_AVAILABLE and FINANCIAL_AVAILABLE) else "partial",
        "mock_components": [
            comp for comp, available in [
                ("fomc", FOMC_AVAILABLE),
                ("financial", FINANCIAL_AVAILABLE)
            ] if not available
        ]
    }

# Example usage:
# result = run_integrated_agent('1010101010', '123456', 'Analyze the March 2024 MPC meeting.', 'What should I do with my portfolio?') 