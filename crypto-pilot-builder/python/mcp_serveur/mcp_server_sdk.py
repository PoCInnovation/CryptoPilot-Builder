#!/usr/bin/env python3
"""
MCP server with OpenAI agent and crypto tools
"""

import asyncio
import sys
import os
import openai
from dotenv import load_dotenv

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

sys.path.append(os.path.dirname(__file__))
from crypto_tools import get_crypto_price

load_dotenv()

class OpenAIAgent:
    """OpenAI Agent"""

    def __init__(self):
        self.client = openai.OpenAI()
        self.model = "gpt-4o-mini"

    async def process_message(self, message: str, context: str = "") -> str:
        """Process message via OpenAI agent"""
        try:
            system_prompt = """You are a crypto expert who responds clearly, structured and pedagogically to questions about cryptocurrencies, their functioning and their investments.
            You can explain how stocks, indices, ETFs, crypto, or any other instrument related to cryptocurrencies work.

            Be rigorous, neutral and didactic. Use concrete examples if it can help understand.
            If you cannot access real-time data, specify it clearly.
            If the question is too vague, ask a clarification question.
            Be transparent with users and don't make mistakes, specify if you don't know how to answer.

            You have to use the get_crypto_price tool to get cryptocurrency prices.

            TOOL USAGE:
            - get_crypto_price(crypto_id, currency="usd"): Get real-time prices
            - Examples: bitcoin, ethereum, dogecoin, cardano, solana, etc.
            - Currencies: usd, eur, gbp (default: usd)

            Use the tool when users ask for prices with keywords like "price", "cost", "how much", "combien", "prix", etc."""

            if context:
                system_prompt += f"\n\nConversation context: {context}"

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7,
                tools=[{
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
                }],
                tool_choice="auto"
            )

            response_message = response.choices[0].message

            # Handle tool calls
            if response_message.tool_calls:
                tool_results = []
                for tool_call in response_message.tool_calls:
                    if tool_call.function.name == "get_crypto_price":
                        import json
                        args = json.loads(tool_call.function.arguments)
                        crypto_id = args.get("crypto_id", "")
                        currency = args.get("currency", "usd")

                        if crypto_id:
                            price_result = get_crypto_price(crypto_id, currency)
                            tool_results.append({
                                "tool_call_id": tool_call.id,
                                "output": price_result
                            })

                # Second call with tool results
                if tool_results:
                    messages = [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message},
                        response_message,
                        {
                            "role": "tool",
                            "content": tool_results[0]["output"],
                            "tool_call_id": tool_results[0]["tool_call_id"]
                        }
                    ]

                    final_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        max_tokens=500,
                        temperature=0.7
                    )

                    return final_response.choices[0].message.content

            return response_message.content

        except Exception as e:
            return f"❌ OpenAI agent error: {str(e)}"

# Agent instance
openai_agent = OpenAIAgent()

# MCP server instance
server = Server("crypto-pilot-agent-server")

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_crypto_price",
            description="Get real-time cryptocurrency price via CoinGecko",
            inputSchema={
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
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[TextContent]:
    """Handle tool calls and agent communication"""

    # Direct crypto price tool call
    if name == "get_crypto_price" and arguments:
        crypto_id = arguments.get("crypto_id", "")
        currency = arguments.get("currency", "usd")

        if crypto_id:
            result = get_crypto_price(crypto_id, currency)
            return [TextContent(type="text", text=result)]
        else:
            return [TextContent(type="text", text="❌ crypto_id required")]

    # General agent communication
    if arguments:
        message = arguments.get("message", "")
        context = arguments.get("context", "")

        if not message:
            message = name if name and name != "agent_chat" else ""

        if not message:
            return [TextContent(type="text", text="❌ Empty message")]

        # Let the agent handle everything including tool detection
        result = await openai_agent.process_message(message, context)
        return [TextContent(type="text", text=result)]

    return [TextContent(type="text", text="❌ Invalid arguments")]

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
    asyncio.run(main())