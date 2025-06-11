#!/usr/bin/env python3
"""
MCP Bridge configuration
"""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent
SERVER_DIR = BASE_DIR.parent / "mcp_serveur"
SERVER_SCRIPT = "mcp_server_sdk.py"

# HTTP server configuration
HOST = "0.0.0.0"
PORT = 5000
DEBUG = True

# MCP configuration
MCP_SERVER_COMMAND = "python"
MCP_SERVER_ARGS = [str(SERVER_DIR / SERVER_SCRIPT)]

# OpenAI configuration (via .env)
OPENAI_MODEL = "gpt-4o-mini"
MAX_TOKENS = 500
TEMPERATURE = 0.7

# Session configuration
MAX_CONTEXT_MESSAGES = 10