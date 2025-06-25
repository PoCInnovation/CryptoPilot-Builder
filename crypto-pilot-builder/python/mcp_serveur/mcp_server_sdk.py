#!/usr/bin/env python3
"""
MCP server with OpenAI agent and crypto tools
"""
import asyncio
import sys
import os
import openai
import json
from dotenv import load_dotenv
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server
sys.path.append(os.path.dirname(__file__))
from crypto_tools import get_crypto_price, request_transaction
load_dotenv()

class OpenAIAgent:
    """OpenAI Agent with crypto capabilities"""
    def __init__(self):
        self.default_client = None  # Client async
        self.model = "gpt-4o-mini"
    
    def _get_default_client(self, api_key=None):
        """Créer un client async seulement quand nécessaire"""
        if self.default_client is None:
            if api_key or os.getenv('OPENAI_API_KEY'):
                actual_api_key = api_key or os.getenv('OPENAI_API_KEY')
                self.default_client = openai.AsyncOpenAI(api_key=actual_api_key)
            else:
                print("Debug: Returning None from _get_default_client (no API key)")  # Debug
                return None
        print("Debug: Returning client from _get_default_client")  # Debug
        return self.default_client
    
    async def process_message(self, message: str, context: str = "") -> str:
        """Process message with default configuration"""
        try:
            client = self._get_default_client()
            if client is None:
                result = "❌ Aucune clé API OpenAI configurée. Veuillez utiliser agent_chat_configured avec votre clé API."
                print(f"Debug: Returning from process_message: {result[:50]}...")  # Debug
                return result
            
            system_prompt = """You are a crypto assistant..."""
            if context:
                system_prompt += f"\nConversation context: {context}"
            
            result = await self._chat_with_openai(message, system_prompt, self.model, client)
            print(f"Debug: Returning from process_message: {result[:50]}...")  # Debug
            return result
        except Exception as e:
            result = f"❌ OpenAI agent error: {str(e)}"
            print(f"Debug: Returning error from process_message: {result}")  # Debug
            return result
    
    async def process_message_with_config(self, message: str, context: str = "", 
                                        system_prompt: str = "", model: str = "gpt-4o-mini", 
                                        api_key: str = "", modules: dict = None) -> str:
        """Process message with custom configuration"""
        try:
            client = self._get_default_client(api_key) if api_key else self._get_default_client()
            if not system_prompt:
                system_prompt = """Tu es un assistant crypto..."""
            
            if modules:
                active_modules = [name for name, active in modules.items() if active]
                if active_modules:
                    system_prompt += f"\nModules activés: {', '.join(active_modules)}"
            
            if context:
                system_prompt += f"\nContexte de conversation: {context}"
            
            result = await self._chat_with_openai(message, system_prompt, model, client)
            print(f"Debug: Returning from process_message_with_config: {result[:50]}...")  # Debug
            return result
        except Exception as e:
            result = f"❌ Erreur agent OpenAI avec configuration: {str(e)}"
            print(f"Debug: Returning error from process_message_with_config: {result}")  # Debug
            return result
    
    async def _chat_with_openai(self, message: str, system_prompt: str, model: str, client=None) -> str:
        """Handle chat with OpenAI including tool calls"""
        if client is None:
            client = self._get_default_client()
            if client is None:
                result = "❌ OpenAI client not configured."
                print(f"Debug: Returning error from _chat_with_openai: {result}")  # Debug
                return result
        
        try:
            print(f"🤖 [OpenAI] Message reçu: {message}")
            print(f"🤖 [OpenAI] System prompt: {system_prompt[:200]}...")
            
            # Détection intelligente des mots-clés de transaction
            transaction_keywords = ["envoie", "envoyer", "send", "transfer", "transférer", "payment", "pay"]
            has_transaction_keyword = any(keyword in message.lower() for keyword in transaction_keywords)
            has_address = "0x" in message and len([part for part in message.split() if part.startswith("0x") and len(part) == 42]) > 0
            has_amount = any(char.isdigit() for char in message)
            is_likely_transaction = has_transaction_keyword and has_address and has_amount
            print(f"🧠 [OpenAI] Détection transaction: keywords={has_transaction_keyword}, address={has_address}, amount={has_amount}, likely={is_likely_transaction}")
            
            # Forcer l'outil de transaction si détecté
            tool_choice = "auto"
            if is_likely_transaction:
                tool_choice = {"type": "function", "function": {"name": "request_transaction"}}
                print(f"🎯 [OpenAI] Forçage de l'outil request_transaction")
            
            # Première requête pour détecter les appels d'outils
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.1,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_crypto_price",
                            "description": "Get real-time cryptocurrency price via CoinGecko API",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "crypto_id": {
                                        "type": "string",
                                        "description": "Cryptocurrency identifier (e.g. bitcoin, ethereum)"
                                    },
                                    "currency": {
                                        "type": "string",
                                        "description": "Desired currency (e.g. eur, usd, gbp)",
                                        "default": "usd"
                                    }
                                },
                                "required": ["crypto_id"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "request_transaction",
                            "description": "Request a blockchain transaction. Use this when user wants to send/transfer cryptocurrency.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "recipient_address": {
                                        "type": "string",
                                        "description": "Recipient Ethereum address (0x...)"
                                    },
                                    "amount": {
                                        "type": "string",
                                        "description": "Amount to send (e.g. 0.001)"
                                    },
                                    "currency": {
                                        "type": "string",
                                        "description": "Network/currency (default: sepolia)",
                                        "default": "sepolia"
                                    }
                                },
                                "required": ["recipient_address", "amount"]
                            }
                        }
                    }
                ],
                tool_choice=tool_choice
            )
            
            response_message = response.choices[0].message
            print(f"🤖 [OpenAI] Response reçue, tool_calls: {hasattr(response_message, 'tool_calls') and response_message.tool_calls}")
            
            # Si des outils sont appelés
            if hasattr(response_message, "tool_calls") and response_message.tool_calls:
                print(f"🤖 [OpenAI] {len(response_message.tool_calls)} outil(s) appelé(s)")
                tool_responses = []
                
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    print(f"🛠️ [OpenAI] Appel outil: {tool_name} avec args: {args}")
                    
                    if tool_name == "get_crypto_price":
                        result = get_crypto_price(
                            args.get("crypto_id", ""),
                            args.get("currency", "usd")
                        )
                        tool_responses.append({
                            "name": tool_name,
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                        print(f"💰 [OpenAI] Prix récupéré: {result[:100]}...")
                    
                    elif tool_name == "request_transaction":
                        result = request_transaction(
                            args.get("recipient_address", ""),
                            args.get("amount", ""),
                            args.get("currency", "sepolia")
                        )
                        tool_responses.append({
                            "name": tool_name,
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                        print(f"🔥 [OpenAI] Transaction générée: {result[:100]}...")
                
                # Si le tool appelé est request_transaction, retourne directement le résultat du tool
                if tool_responses:
                    for res in tool_responses:
                        if res["name"] == "request_transaction":
                            print("🚩 [OpenAI] Retour direct du résultat request_transaction au front")
                            return res["content"]  # string JSON déjà formaté
                    # Sinon, on continue avec la deuxième requête OpenAI (pour les autres tools)
                    second_messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message},
                        {"role": "assistant", "content": None, "tool_calls": response_message.tool_calls},
                    ]
                    for res in tool_responses:
                        second_messages.append({
                            "role": "tool",
                            "name": res["name"],
                            "content": res["content"],
                            "tool_call_id": res["tool_call_id"]
                        })
                    second_response = await client.chat.completions.create(
                        model=model,
                        messages=second_messages,
                        max_tokens=500,
                        temperature=0.1
                    )
                    
                    final_response = second_response.choices[0].message.content
                    print(f"Debug: Returning final response from _chat_with_openai: {final_response[:50]}...")  # Debug
                    return final_response
            
            # Pas d'outils appelés - réponse directe
            direct_response = response_message.content
            print(f"Debug: Returning direct response from _chat_with_openai: {direct_response[:50]}...")  # Debug
            return direct_response
        
        except Exception as e:
            result = f"❌ Error in chat: {str(e)}"
            print(f"Debug: Returning error from _chat_with_openai: {result}")  # Debug
            return result

# Agent instance
openai_agent = OpenAIAgent()

# MCP server instance
server = Server("crypto-pilot-agent-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    print("Debug: Returning from handle_list_tools (tools list)")  # Debug
    return [
        Tool(
            name="get_crypto_price",
            description="Get real-time cryptocurrency price via CoinGecko",
            inputSchema={
                "type": "object",
                "properties": {
                    "crypto_id": {
                        "type": "string",
                        "description": "Cryptocurrency identifier"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Desired currency (default: usd)",
                        "default": "usd"
                    }
                },
                "required": ["crypto_id"]
            }
        ),
        Tool(
            name="request_transaction",
            description="Request a blockchain transaction",
            inputSchema={
                "type": "object",
                "properties": {
                    "recipient_address": {
                        "type": "string",
                        "description": "Ethereum recipient address"
                    },
                    "amount": {
                        "type": "string",
                        "description": "Amount to send"
                    },
                    "currency": {
                        "type": "string",
                        "description": "Network/currency (default: sepolia)",
                        "default": "sepolia"
                    }
                },
                "required": ["recipient_address", "amount"]
            }
        ),
        Tool(
            name="agent_chat_configured",
            description="Chat with AI agent using custom configuration",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "User message"
                    },
                    "context": {
                        "type": "string",
                        "description": "Conversation context"
                    },
                    "system_prompt": {
                        "type": "string",
                        "description": "Custom system prompt"
                    },
                    "model": {
                        "type": "string",
                        "description": "OpenAI model to use",
                        "default": "gpt-4o-mini"
                    },
                    "api_key": {
                        "type": "string",
                        "description": "User's OpenAI API key"
                    },
                    "modules": {
                        "type": "string",
                        "description": "JSON string of enabled modules"
                    }
                },
                "required": ["message"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Handle tool calls and agent communication"""
    if arguments is None:
        result = [TextContent(type="text", text="❌ Invalid arguments")]
        print("Debug: Returning from handle_call_tool (invalid arguments)")  # Debug
        return result
    
    # Direct crypto price tool call
    if name == "get_crypto_price":
        crypto_id = arguments.get("crypto_id", "")
        currency = arguments.get("currency", "usd")
        if crypto_id:
            result = get_crypto_price(crypto_id, currency)
            print(f"Debug: Returning from get_crypto_price: {result[:50]}...")  # Debug
            return [TextContent(type="text", text=result)]
        result = [TextContent(type="text", text="❌ crypto_id required")]
        print("Debug: Returning from get_crypto_price (missing crypto_id)")  # Debug
        return result
    
    if name == "request_transaction":
        recipient_address = arguments.get("recipient_address", "")
        amount = arguments.get("amount", "")
        currency = arguments.get("currency", "sepolia")
        if recipient_address and amount:
            result = request_transaction(recipient_address, amount, currency)
            print(f"Debug: Returning from request_transaction: {result[:50]}...")  # Debug
            return [TextContent(type="text", text=result)]
        result = [TextContent(type="text", text="❌ recipient_address and amount required")]
        print("Debug: Returning from request_transaction (missing fields)")  # Debug
        return result
    
    if name == "agent_chat_configured":
        message = arguments.get("message", "")
        context = arguments.get("context", "")
        system_prompt = arguments.get("system_prompt", "")
        model = arguments.get("model", "gpt-4o-mini")
        api_key = arguments.get("api_key", "")
        modules_str = arguments.get("modules", "{}")
        modules = {}
        try:
            modules = json.loads(modules_str) if modules_str else {}
        except:
            modules = {}
        
        if not message:
            result = [TextContent(type="text", text="❌ Empty message")]
            print("Debug: Returning from agent_chat_configured (empty message)")  # Debug
            return result
        
        result = await openai_agent.process_message_with_config(
            message=message,
            context=context,
            system_prompt=system_prompt,
            model=model,
            api_key=api_key,
            modules=modules
        )
        print(f"Debug: Returning from agent_chat_configured: {result[:50]}...")  # Debug
        return [TextContent(type="text", text=result)]
    
    # General agent communication
    message = arguments.get("message", "")
    context = arguments.get("context", "")
    if not message:
        message = name if name and name != "agent_chat" else ""
    if not message:
        result = [TextContent(type="text", text="❌ Empty message")]
        print("Debug: Returning from handle_call_tool (empty message)")  # Debug
        return result
    
    result = await openai_agent.process_message(message, context)
    print(f"Debug: Returning from handle_call_tool: {result[:50]}...")  # Debug
    return [TextContent(type="text", text=result)]

async def main():
    """Launch MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="crypto-pilot-agent-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    print("✅ DEBUG MODE ACTIF")
    asyncio.run(main())