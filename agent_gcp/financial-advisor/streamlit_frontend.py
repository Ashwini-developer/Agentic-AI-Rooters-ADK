"""
Streamlit Frontend for Financial Advisor Trading Analyst
Integrates with FastAPI backend
"""

import streamlit as st
import requests
import json
from datetime import datetime
import time

# Configure Streamlit page
st.set_page_config(
    page_title="Financial Advisor Trading Analyst",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'phone_number' not in st.session_state:
    st.session_state.phone_number = None

def make_api_request(endpoint, method="GET", data=None):
    """Make API request with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=30)
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API server. Please ensure the FastAPI server is running on port 8000.")
        st.info("💡 **To start the server:**\n```\npython api_server.py\n```")
        return None
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The analysis might be taking longer than expected.")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"❌ API Error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None

def check_api_health():
    """Check if API server is running"""
    result = make_api_request("/health")
    return result is not None

def get_api_status():
    """Get detailed API status"""
    return make_api_request("/status")

def authenticate_user(phone_number, otp):
    """Authenticate user with API"""
    data = {
        "phone_number": phone_number,
        "otp": otp
    }
    
    result = make_api_request("/authenticate", method="POST", data=data)
    
    if result and result.get('authenticated'):
        st.session_state.authenticated = True
        st.session_state.phone_number = phone_number
        return True
    
    return False

def get_test_users():
    """Get available test users from API"""
    result = make_api_request("/users")
    if result:
        return result.get('test_users', [])
    return []

def get_integrated_analysis(phone_number, otp, mpc_prompt, fin_prompt):
    """Get integrated analysis from API"""
    data = {
        "phone_number": phone_number,
        "otp": otp,
        "mpc_prompt": mpc_prompt,
        "fin_prompt": fin_prompt
    }
    
    return make_api_request("/integrated_analysis", method="POST", data=data)

# Main UI
st.title("🏦 Financial Advisor + FOMC Research Integration")
st.markdown("### AI-Powered Integrated Financial Analysis")

# Check API health
api_healthy = check_api_health()

if not api_healthy:
    st.error("🚨 **API Server is not running or not responding**")
    st.markdown("**Please start the FastAPI server first:**")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.code("python api_server.py", language="bash")
    with col2:
        st.code("python start_integrated_app.py", language="bash")
    
    st.info("📍 The API server should be running on **http://localhost:8000**")
    
    if st.button("🔄 Retry Connection"):
        st.rerun()
    
    st.stop()

# Sidebar for API status and info
with st.sidebar:
    st.markdown("## 🔧 System Status")
    
    # Get detailed API status
    api_status = get_api_status()
    if api_status:
        st.success("✅ API Server: Online")
        
        # Show integration status
        integration_status = api_status.get('integration_status', {})
        
        if integration_status.get('integration_mode') == 'full':
            st.success("🔗 Integration: Full Mode")
        elif integration_status.get('integration_mode') == 'mock':
            st.warning("🎭 Integration: Mock Mode")
        else:
            st.info("🔄 Integration: Partial Mode")
        
        # Show component status
        st.markdown("**Component Status:**")
        fomc_status = "✅" if integration_status.get('fomc_available') else "❌"
        financial_status = "✅" if integration_status.get('financial_available') else "❌"
        
        st.markdown(f"- FOMC Agent: {fomc_status}")
        st.markdown(f"- Financial Agent: {financial_status}")
        
        if integration_status.get('mock_components'):
            st.markdown(f"**Mock Components:** {', '.join(integration_status['mock_components'])}")
    else:
        st.error("❌ API Server: Offline")
    
    st.markdown("## 📋 Available Features")
    st.markdown("""
    - 🔐 **Authentication**: Secure phone + OTP login
    - 🏛️ **FOMC Research**: Monetary policy analysis
    - 💰 **Financial Advisory**: Investment recommendations
    - 🔗 **Integrated Analysis**: Combined insights
    """)
    
    # Show test users
    st.markdown("## 👥 Test Users")
    test_users = get_test_users()
    if test_users:
        st.markdown("**Available Phone Numbers:**")
        for user in test_users[:3]:  # Show first 3
            st.markdown(f"- {user['phone_number']}")
        if len(test_users) > 3:
            st.markdown(f"... and {len(test_users) - 3} more")
    else:
        st.markdown("- 1010101010\n- 2020202020\n- 3030303030")
    
    st.markdown("**Demo OTP:** `123456`")

# Authentication Section
if not st.session_state.authenticated:
    st.markdown("## 🔐 Authentication Required")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.form("auth_form"):
            st.markdown("#### Enter your credentials")
            
            phone_number = st.text_input(
                "Phone Number (10 digits)",
                placeholder="1010101010",
                help="Must match a test user in the system"
            )
            
            otp = st.text_input(
                "OTP",
                type="password",
                placeholder="123456",
                help="Demo OTP is: 123456"
            )
            
            submitted = st.form_submit_button("🔓 Login", use_container_width=True)
    
    with col2:
        st.markdown("#### Quick Login")
        st.info("💡 **Demo Credentials:**\n\n📱 Phone: `1010101010`\n🔐 OTP: `123456`")
        
        if st.button("🚀 Quick Login", use_container_width=True):
            if authenticate_user("1010101010", "123456"):
                st.success("✅ Quick login successful!")
                st.rerun()
    
    if submitted:
        if not phone_number or not otp:
            st.error("❌ Please enter both phone number and OTP")
        elif len(phone_number) != 10 or not phone_number.isdigit():
            st.error("❌ Phone number must be exactly 10 digits")
        else:
            with st.spinner("🔄 Authenticating..."):
                if authenticate_user(phone_number, otp):
                    st.success("✅ Authentication successful!")
                    st.rerun()
                else:
                    st.error("❌ Authentication failed. Please check your credentials.")

# Main Application (after authentication)
else:
    st.success(f"✅ Logged in as: {st.session_state.phone_number}")
    
    # Logout button
    if st.button("🚪 Logout", key="logout"):
        st.session_state.authenticated = False
        st.session_state.session_id = None
        st.session_state.phone_number = None
        st.rerun()
    
    st.markdown("---")
    
    # Main Analysis Interface
    st.markdown("### 🔗 Integrated FOMC + Financial Analysis")
    st.markdown("Combine monetary policy research with personalized financial advice based on your portfolio data.")
    
    with st.form("integrated_analysis_form"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 🏛️ FOMC Research Query")
            mpc_prompt = st.text_area(
                "What would you like to know about monetary policy?",
                placeholder="Analyze the latest Federal Reserve policy decisions and their impact on financial markets.",
                height=120,
                help="Ask about interest rates, monetary policy decisions, economic outlook, FOMC meetings, etc."
            )
        
        with col2:
            st.markdown("#### 💰 Financial Advisory Query")
            fin_prompt = st.text_area(
                "What financial advice do you need?",
                placeholder="Based on current monetary policy, how should I adjust my investment portfolio?",
                height=120,
                help="Ask about portfolio management, investment strategies, risk assessment, etc."
            )
        
        # Analysis options
        st.markdown("#### ⚙️ Analysis Options")
        col3, col4 = st.columns([1, 1])
        
        with col3:
            include_portfolio = st.checkbox("📊 Include Portfolio Analysis", value=True, help="Use your personal financial data")
        
        with col4:
            detailed_mode = st.checkbox("🔍 Detailed Analysis", value=False, help="Get more comprehensive insights")
        
        submitted = st.form_submit_button("🚀 Generate Integrated Analysis", use_container_width=True)

    if submitted:
        if not mpc_prompt.strip() or not fin_prompt.strip():
            st.error("❌ Please provide both FOMC and Financial queries")
        else:
            with st.spinner("🔄 Running integrated analysis... This may take a moment."):
                # Add progress indicator
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.text("🏛️ Analyzing monetary policy...")
                progress_bar.progress(25)
                time.sleep(0.5)
                
                status_text.text("💰 Generating financial recommendations...")
                progress_bar.progress(50)
                
                result = get_integrated_analysis(
                    st.session_state.phone_number,
                    "123456",  # Demo OTP
                    mpc_prompt,
                    fin_prompt
                )
                
                progress_bar.progress(75)
                status_text.text("🔗 Integrating insights...")
                time.sleep(0.5)
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
                
                # Clear progress indicators
                progress_bar.empty()
                status_text.empty()
                
                if result and result.get('success', True):
                    st.markdown("---")
                    st.markdown("### 🎯 Integrated Analysis Results")
                    
                    # Display analysis
                    analysis = result.get('result', result)
                    if isinstance(analysis, str):
                        st.markdown(analysis)
                    else:
                        st.write(analysis)
                    
                    # Show metadata in expandable section
                    with st.expander("📋 Analysis Details", expanded=False):
                        metadata = {
                            "FOMC Query": result.get('mpc_prompt', mpc_prompt),
                            "Financial Query": result.get('financial_prompt', fin_prompt),
                            "Analysis Type": result.get('analysis_type', 'integrated'),
                            "Timestamp": result.get('timestamp', datetime.now().isoformat()),
                            "Portfolio Analysis": "Included" if include_portfolio else "Excluded",
                            "Analysis Mode": "Detailed" if detailed_mode else "Standard"
                        }
                        
                        for key, value in metadata.items():
                            st.markdown(f"**{key}:** {value}")
                    
                    # Download options
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        analysis_text = analysis if isinstance(analysis, str) else str(analysis)
                        st.download_button(
                            label="📥 Download Full Report",
                            data=analysis_text,
                            file_name=f"integrated_analysis_{st.session_state.phone_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                    
                    with col2:
                        # Create summary for download
                        summary = f"""
# Financial Analysis Summary

**User:** {st.session_state.phone_number}
**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**FOMC Query:** {mpc_prompt}
**Financial Query:** {fin_prompt}

**Key Insights:** [Analysis completed - see full report for details]
                        """
                        
                        st.download_button(
                            label="📄 Download Summary",
                            data=summary,
                            file_name=f"analysis_summary_{st.session_state.phone_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                            mime="text/markdown",
                            use_container_width=True
                        )
                
                else:
                    st.error("❌ Failed to get integrated analysis.")
                    if result:
                        st.error(f"Error details: {result}")
                    st.info("💡 Please try again or contact support if the issue persists")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em; padding: 10px;'>
    🤖 Powered by FastAPI + Streamlit | 
    🏦 Financial Advisor + FOMC Research Integration System<br>
    📊 Combining Monetary Policy Analysis with Personalized Financial Advice
    </div>
    """, 
    unsafe_allow_html=True
)
