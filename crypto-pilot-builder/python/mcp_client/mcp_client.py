#!/usr/bin/env python3
"""
Client MCP pur - Gestion de la connexion et communication avec le serveur MCP
"""

import asyncio
from typing import Dict, Any, List
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from config import MCP_SERVER_COMMAND, MCP_SERVER_ARGS

class MCPClient:
    def __init__(self):
        self.server_params = None
        self.connected = False

    async def connect(self) -> bool:
        """Configure la connexion au serveur MCP"""
        if self.connected:
            return True

        try:
            self.server_params = StdioServerParameters(
                command=MCP_SERVER_COMMAND,
                args=MCP_SERVER_ARGS,
            )

            self.connected = True
            print("✅ Client MCP configuré pour connexion")
            return True

        except Exception as e:
            print(f"❌ Erreur configuration MCP: {e}")
            return False

    async def ensure_connection(self) -> bool:
        """S'assure qu'on a une connexion configurée"""
        if not self.connected:
            await self.connect()
        return self.connected

    async def list_tools(self) -> Dict[str, Any]:
        """Liste les outils disponibles via MCP"""
        await self.ensure_connection()

        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools = await session.list_tools()
                    return {
                        "tools": [tool.model_dump() for tool in tools.tools],
                        "count": len(tools.tools)
                    }
        except Exception as e:
            return {"error": f"Erreur list_tools: {str(e)}"}

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Appelle un outil via MCP"""
        await self.ensure_connection()

        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)

                    # Extrait le texte de la réponse
                    if result.content and len(result.content) > 0:
                        return {
                            "result": result.content[0].text,
                            "success": True
                        }
                    else:
                        return {
                            "result": "Aucun résultat",
                            "success": False
                        }

        except Exception as e:
            return {
                "error": f"Erreur call_tool: {str(e)}",
                "success": False
            }

    async def chat(self, message: str, context: str = "") -> Dict[str, Any]:
        """Méthode helper pour le chat via l'outil chat_openai"""
        return await self.call_tool("chat_openai", {
            "message": message,
            "context": context
        })

    def is_connected(self) -> bool:
        """Vérifie si le client est configuré"""
        return self.connected

# Instance globale
mcp_client = MCPClient()