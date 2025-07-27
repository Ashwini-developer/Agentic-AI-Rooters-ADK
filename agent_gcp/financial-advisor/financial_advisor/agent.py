# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Financial coordinator: provide reasonable investment strategies"""

import os
import json
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.data_analyst import data_analyst_agent
from .sub_agents.execution_analyst import execution_analyst_agent
from .sub_agents.risk_analyst import risk_analyst_agent
from .sub_agents.trading_analyst import trading_analyst_agent

import re

MODEL = "gemini-2.5-pro"


def is_valid_phone_number(phone_number):
    """Check if phone number is 10 digits and matches a test_data_dir subfolder."""
    if not (isinstance(phone_number, str) and phone_number.isdigit() and len(phone_number) == 10):
        return False
    test_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'test_data_dir')
    test_data_dir = os.path.abspath(test_data_dir)
    return phone_number in os.listdir(test_data_dir)

class FinancialCoordinatorWithAuth(LlmAgent):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._auth_state = {}

    def choose_tool(self, input_data, state):
        """Choose which subagent/tool to invoke based on user input."""
        text = input_data.lower() if isinstance(input_data, str) else ""
        # Simple keyword-based intent detection
        if any(word in text for word in ["analyze", "market", "ticker", "stock", "data analysis"]):
            return "data_analyst_agent"
        if any(word in text for word in ["strategy", "strategies", "trading", "risk attitude", "investment period"]):
            return "trading_analyst_agent"
        if any(word in text for word in ["execution", "order", "broker", "plan", "entry", "exit"]):
            return "execution_analyst_agent"
        if any(word in text for word in ["risk", "evaluate", "assessment", "profile"]):
            return "risk_analyst_agent"
        return None

    def run(self, input_data, state=None, **kwargs):
        state = state or {}
        # Step 1: Ask for phone number if not present
        if 'phone_number' not in state:
            return {
                'output': "Hello! Please enter your 10-digit phone number to continue:",
                'state': state
            }
        # Step 2: Validate phone number
        phone_number = state['phone_number']
        if not is_valid_phone_number(phone_number):
            return {
                'output': "Invalid phone number. Please enter a valid 10-digit phone number registered with us:",
                'state': {k: v for k, v in state.items() if k != 'phone_number'}
            }
        # Step 3: Ask for OTP if not present
        if 'otp' not in state:
            return {
                'output': f"An OTP has been sent to {phone_number}. Please enter the 6-digit OTP:",
                'state': state
            }
        # Step 4: Validate OTP
        if state['otp'] != '123456':
            return {
                'output': "Invalid OTP. Please try again:",
                'state': {**state, 'otp': None}
            }
        # Step 5: Load user data and proceed to normal flow
        user_data = state.get('user_data')
        mpc_fields = ['mpc_research_output', 'geopolitical_news', 'macroeconomic_news', 'microeconomic_news', 'flight_log_details', 'local_political_news']
        mpc_data = {k: state.get(k, '') for k in mpc_fields}
        if not user_data:
            # Load all JSON files from the user's test_data_dir subfolder
            test_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', '..', 'test_data_dir')
            user_dir = os.path.join(test_data_dir, phone_number)
            user_data = {}
            for fname in os.listdir(user_dir):
                if fname.endswith('.json'):
                    fpath = os.path.join(user_dir, fname)
                    with open(fpath, 'r', encoding='utf-8') as f:
                        key = fname.replace('.json', '')
                        try:
                            user_data[key] = json.load(f)
                        except Exception:
                            user_data[key] = None
            state['user_data'] = user_data
        # Remove auth keys from state for downstream agents
        clean_state = {k: v for k, v in state.items() if k not in ('phone_number', 'otp')}
        clean_state['user_data'] = user_data
        for k, v in mpc_data.items():
            clean_state[k] = v
        # Dynamic tool selection
        tool_name = self.choose_tool(input_data, clean_state)
        if tool_name:
            for tool in self.tools:
                if hasattr(tool, 'agent') and getattr(tool.agent, 'name', None) == tool_name:
                    # Call the selected subagent/tool
                    return tool.agent.run(input_data, state=clean_state, **kwargs)
        # Fallback: default to normal LlmAgent behavior
        return super().run(input_data, state=clean_state, **kwargs)

financial_coordinator = FinancialCoordinatorWithAuth(
    name="financial_coordinator",
    model=MODEL,
    description=(
        "guide users through a structured process to receive financial "
        "advice by orchestrating a series of expert subagents. help them "
        "analyze a market ticker, develop trading strategies, define "
        "execution plans, and evaluate the overall risk."
    ),
    instruction=prompt.FINANCIAL_COORDINATOR_PROMPT,
    output_key="financial_coordinator_output",
    tools=[
        AgentTool(agent=data_analyst_agent),
        AgentTool(agent=trading_analyst_agent),
        AgentTool(agent=execution_analyst_agent),
        AgentTool(agent=risk_analyst_agent),
    ],
)

root_agent = financial_coordinator
