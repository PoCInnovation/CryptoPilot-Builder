#!/usr/bin/env python3
"""
Base interface for all AI agents
"""
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for all AI agents with crypto capabilities"""

    @abstractmethod
    async def process_message(self, message: str, context: str = "") -> str:
        """Process a message with default configuration"""
        pass

    @abstractmethod
    async def process_message_with_config(self, message: str, context: str = "",
        system_prompt: str = "", model: str = "",
        api_key: str = "", modules: dict = None) -> str:
        """Process a message with custom configuration"""
        pass
