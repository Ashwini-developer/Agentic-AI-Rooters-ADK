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

"""Research coordinator agent for FOMC Research Agent."""

from google.adk.agents import Agent

from ..agent import MODEL
from ..shared_libraries.callbacks import rate_limit_callback
from ..tools.compare_statements import compare_statements_tool
from ..tools.compute_rate_move_probability import compute_rate_move_probability_tool
from ..tools.fetch_transcript import fetch_transcript_tool
from ..tools.store_state import store_state_tool
from ..tools.fetch_page import (
    fetch_geopolitical_news,
    fetch_macroeconomic_news,
    fetch_microeconomic_news,
    fetch_flight_log_details,
    fetch_local_political_news,
)
from . import research_agent_prompt
from .summarize_meeting_agent import SummarizeMeetingAgent

async def research_agent_run(tool_context):
    # Existing steps (compare statements, fetch transcript, etc.)
    # ...
    # New: Fetch and store news and flight log details
    geo = fetch_geopolitical_news(tool_context)
    tool_context.state['geopolitical_news'] = tool_context.state.get('page_contents', '')
    macro = fetch_macroeconomic_news(tool_context)
    tool_context.state['macroeconomic_news'] = tool_context.state.get('page_contents', '')
    micro = fetch_microeconomic_news(tool_context)
    tool_context.state['microeconomic_news'] = tool_context.state.get('page_contents', '')
    flight = fetch_flight_log_details(tool_context)
    tool_context.state['flight_log_details'] = tool_context.state.get('page_contents', '')
    local = fetch_local_political_news(tool_context)
    tool_context.state['local_political_news'] = tool_context.state.get('page_contents', '')
    # ... continue with rest of agent logic

ResearchAgent = Agent(
    model=MODEL,
    name="research_agent",
    description=(
        "Research the latest MPC meeting and all relevant contextual news to provide information for analysis."
    ),
    instruction=research_agent_prompt.PROMPT,
    sub_agents=[
        SummarizeMeetingAgent,
    ],
    tools=[
        store_state_tool,
        compare_statements_tool,
        fetch_transcript_tool,
        compute_rate_move_probability_tool,
        fetch_geopolitical_news,
        fetch_macroeconomic_news,
        fetch_microeconomic_news,
        fetch_flight_log_details,
        fetch_local_political_news,
    ],
    before_model_callback=rate_limit_callback,
    run=research_agent_run,
)
