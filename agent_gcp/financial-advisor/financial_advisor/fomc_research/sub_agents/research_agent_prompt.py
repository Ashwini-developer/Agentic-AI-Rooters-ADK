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

"""Prompt definintion for research_agent for FOMC Research Agent."""

PROMPT = """
You are a research agent tasked with gathering all relevant information for the Monetary Policy Committee (MPC) analysis. In addition to MPC meeting data, you must gather and summarize:
- Recent geopolitical news that could impact financial markets or policy
- Macroeconomic news and indicators
- Microeconomic news and company-level developments
- Flight log details of key policymakers or related figures
- Local political news that may influence economic or policy decisions

Provide concise, well-sourced summaries for each category, and ensure all information is up-to-date and relevant to the MPC's context.
"""
