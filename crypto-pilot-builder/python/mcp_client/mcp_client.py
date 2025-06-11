#!/usr/bin/env python3
"""
MCP client for communication with OpenAI crypto agent
"""

import asyncio
from typing import Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from config import MCP_SERVER_COMMAND, MCP_SERVER_ARGS

class MCPClient:
    """MCP client for crypto agent"""

    def __init__(self):
        self.server_params = None
        self.connected = False

    async def connect(self) -> bool:
        """Configure connection to MCP server"""
        if self.connected:
            return True

        try:
            self.server_params = StdioServerParameters(
                command=MCP_SERVER_COMMAND,
                args=MCP_SERVER_ARGS,
            )
            self.connected = True
            print("✅ MCP client configured for connection")
            return True

        except Exception as e:
            print(f"❌ MCP configuration error: {e}")
            return False

    async def ensure_connection(self) -> bool:
        """Ensure we have a configured connection"""
        if not self.connected:
            await self.connect()
        return self.connected

    async def list_tools(self) -> Dict[str, Any]:
        """List available tools via MCP"""
        await self.ensure_connection()

        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    return {
                        "tools": [tool.model_dump() for tool in tools.tools],
                        "count": len(tools.tools),
                        "agent": "OpenAI CryptoPilot Agent",
                        "note": "Crypto tools available"
                    }
        except Exception as e:
            return {"error": f"list_tools error: {str(e)}"}

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool or communicate with agent"""
        await self.ensure_connection()

        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)

                    if result.content and len(result.content) > 0:
                        return {
                            "result": result.content[0].text,
                            "success": True,
                            "agent": "OpenAI"
                        }
                    else:
                        return {
                            "result": "No result",
                            "success": False
                        }

        except Exception as e:
            return {
                "error": f"call_tool error: {str(e)}",
                "success": False
            }

    async def get_crypto_price(self, crypto_id: str, currency: str = "usd") -> Dict[str, Any]:
        """Get crypto price via MCP tool"""
        return await self.call_tool("get_crypto_price", {
            "crypto_id": crypto_id,
            "currency": currency
        })

    async def chat(self, message: str, context: str = "") -> Dict[str, Any]:
        """Communication with OpenAI agent"""
        return await self.call_tool("agent_chat", {
            "message": message,
            "context": context
        })

    def is_connected(self) -> bool:
        """Check if client is configured"""
        return self.connected

# Global instance
mcp_client = MCPClient()