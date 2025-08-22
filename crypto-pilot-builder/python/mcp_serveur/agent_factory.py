#!/usr/bin/env python3
"""
Factory for creating AI agents based on provider
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))
from base_agent import BaseAgent

class AgentFactory:
    """Factory for creating AI agents"""

    @staticmethod
    def create_agent(provider: str = "openai") -> BaseAgent:
        """
        Create an AI agent based on the provider

        Args:
            provider (str): The AI provider to use (default: "openai")

        Returns:
            BaseAgent: An instance of the appropriate agent
        """
        if provider.lower() == "openai":
            from mcp_server_sdk import OpenAIAgent
            return OpenAIAgent()
        else:
            # Fallback to OpenAI for now
            print(f"⚠️ Provider '{provider}' not yet implemented, falling back to OpenAI")
            from mcp_server_sdk import OpenAIAgent
            return OpenAIAgent()

    @staticmethod
    def get_available_providers() -> list:
        """Get list of available providers"""
        return ["openai"]
