#!/usr/bin/env python3
"""
HTTP-MCP Bridge entry point
Orchestrates all modules to create the complete API
"""

import asyncio
from flask import Flask
from flask_cors import CORS

# Local modules imports
from .config import HOST, PORT, DEBUG
from .mcp_client import mcp_client
from .session_manager import session_manager
from .api_routes import create_api_routes

def create_app():
    """Factory to create Flask application"""
    app = Flask(__name__)
    CORS(app)

    # Register routes
    create_api_routes(app)

    return app

async def init_mcp():
    """Initialize MCP client at startup"""
    success = await mcp_client.connect()
    if success:
        print("✅ MCP client initialized successfully")
    else:
        print("❌ MCP initialization failed")
    return success

def main():
    """Main entry point"""
    print("🌉 HTTP-MCP Bridge - Modular version")
    print("📁 Structure:")
    print("  ├── config.py           # Configuration")
    print("  ├── mcp_client.py       # Pure MCP client")
    print("  ├── session_manager.py  # Session management")
    print("  ├── api_routes.py       # API routes")
    print("  └── mcp_http_bridge.py  # Entry point")
    print()

    # MCP initialization
    print("🔧 Initializing MCP client...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    mcp_ready = loop.run_until_complete(init_mcp())
    loop.close()

    if not mcp_ready:
        print("❌ Cannot start without MCP")
        return

    # Application creation
    app = create_app()

    print(f"🚀 API available on http://{HOST}:{PORT}")
    print("💡 Main endpoints:")
    print("  - POST /chat           # Frontend chat")
    print("  - POST /new-session    # New session")
    print("  - GET  /health         # Service status")
    print("  - GET  /mcp/tools      # MCP tools")
    print()

    # Server startup
    app.run(debug=DEBUG, host=HOST, port=PORT)

if __name__ == "__main__":
    main()