#!/usr/bin/env python3
"""
Serveur MCP officiel avec SDK Python
Outils: crypto prices + OpenAI chat
"""

import asyncio
import sys
from typing import Any, Sequence
import openai
from dotenv import load_dotenv

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)
from mcp.server.stdio import stdio_server

load_dotenv()

# Instance OpenAI
openai_client = openai.OpenAI()

# Instance du serveur MCP
server = Server("crypto-mcp-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Retourne la liste des outils disponibles"""
    return [
        Tool(
            name="chat_openai",
            description="Conversation avec OpenAI GPT",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string", 
                        "description": "Message de l'utilisateur"
                    },
                    "context": {
                        "type": "string",
                        "description": "Contexte de la conversation (optionnel)"
                    }
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Exécute un outil MCP"""
    
    if name == "chat_openai":
        message = arguments.get("message", "")
        context = arguments.get("context", "")
        
        try:
            # Prompt système spécialisé crypto
            system_prompt = """Tu es un expert en cryptomonnaies et finance décentralisée. 
            Tu réponds de manière claire, précise et pédagogique. 
            Tu peux expliquer les concepts techniques, analyser les marchés, 
            et donner des informations sur les projets blockchain.
            Sois neutre et factuel, évite les conseils financiers directs."""
            
            if context:
                system_prompt += f"\n\nContexte: {context}"
            
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            result = response.choices[0].message.content
            
        except Exception as e:
            result = f"❌ Erreur OpenAI: {str(e)}"
            
        return [TextContent(type="text", text=result)]
    
    else:
        return [TextContent(type="text", text=f"❌ Outil '{name}' non reconnu")]

async def main():
    """Lance le serveur MCP avec stdio"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="crypto-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main()) 