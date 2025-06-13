#!/bin/bash

# Check if uv is installed, if not install it
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Run the application with uv
echo "Setting up environment and running the application..."
uv run --with-requirements requirements.txt --isolated ./mcp_client/mcp_http_bridge.py