#!/usr/bin/env python3
"""
Configuration pour le bridge MCP
"""

import os
from pathlib import Path

# Chemins
BASE_DIR = Path(__file__).parent
SERVER_DIR = BASE_DIR.parent / "mcp_serveur"
SERVER_SCRIPT = "mcp_server_sdk.py"

# Configuration serveur HTTP
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True

# Configuration MCP
MCP_SERVER_COMMAND = "python"
MCP_SERVER_ARGS = [str(SERVER_DIR / SERVER_SCRIPT)]

# Configuration OpenAI (via .env)
OPENAI_MODEL = "gpt-4o-mini"
MAX_TOKENS = 500
TEMPERATURE = 0.7

# Configuration sessions
MAX_CONTEXT_MESSAGES = 10