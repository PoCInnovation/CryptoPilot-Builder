#!/usr/bin/env python3
"""
Main Flask application entry point
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from mcp_client.mcp_http_bridge import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
