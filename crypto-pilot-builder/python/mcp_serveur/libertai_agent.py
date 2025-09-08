#!/usr/bin/env python3
"""
LibertAI Agent with crypto capabilities
"""
import asyncio
import sys
import os
import json
from dotenv import load_dotenv
from base_agent import BaseAgent
sys.path.append(os.path.dirname(__file__))
from crypto_tools import get_crypto_price, request_transaction, get_lifi_tokens, get_swap_quote, execute_swap, get_sepolia_tokens, get_all_erc20_tokens
load_dotenv()

class LibertAIAgent(BaseAgent):
    """LibertAI Agent with crypto capabilities"""

    def __init__(self):
        self.base_url = "https://api.libertai.io/v1"
        self.model = "gemma-3-27b"
        self.api_key = None
        self.client = None

    def _get_client(self, api_key=None):
        """Create LibertAI client (OpenAI-compatible)"""
        try:
            import openai
            actual_api_key = api_key or os.getenv('LIBERTAI_API_KEY')
            if not actual_api_key:
                print("❌ Aucune clé API LibertAI fournie")
                return None
            print(f"🔑 Création du client LibertAI avec l'endpoint: {self.base_url}")
            print(f"🔑 Clé API: {actual_api_key[:10]}...{actual_api_key[-4:] if len(actual_api_key) > 14 else '***'}")
            client = openai.AsyncOpenAI(
                api_key=actual_api_key,
                base_url=self.base_url
            )
            print("✅ Client LibertAI créé avec succès")
            return client
        except ImportError as e:
            print(f"❌ Erreur d'import openai: {e}")
            return None
        except Exception as e:
            print(f"❌ Erreur lors de la création du client LibertAI: {e}")
            return None

    async def process_message(self, message: str, context: str = "") -> str:
        """Process message with default configuration"""
        try:
            client = self._get_client()
            if client is None:
                return "❌ Aucune clé API LibertAI configurée. Veuillez utiliser agent_chat_configured avec votre clé API LibertAI."
            system_prompt = self.get_shared_system_prompt()
            if context:
                system_prompt = self.append_modules_and_context(system_prompt, context)
            result = await self._chat_with_libertai(message, system_prompt, self.model, client)
            return result
        except Exception as e:
            return f"❌ LibertAI agent error: {str(e)}"

    async def process_message_with_config(self, message: str, context: str = "",
                                        system_prompt: str = "", model: str = "hermes-3-8b",
                                        api_key: str = "", modules: dict = None) -> str:
        """Process message with custom configuration"""
        try:
            client = self._get_client(api_key) if api_key else self._get_client()
            if not client:
                return "❌ LibertAI client not configured. Please provide a valid API key."
            if not system_prompt:
                system_prompt = self.get_shared_system_prompt()
            system_prompt = self.append_modules_and_context(system_prompt, context, modules)
            result = await self._chat_with_libertai(message, system_prompt, model, client)
            return result
        except Exception as e:
            return f"❌ Erreur agent LibertAI avec configuration: {str(e)}"

    async def _chat_with_libertai(self, message: str, system_prompt: str, model: str, client=None) -> str:
        """Handle chat with LibertAI including tool calls"""
        if client is None:
            client = self._get_client()
            if client is None:
                return "❌ LibertAI client not configured."
        try:
            print(f"🔍 DEBUG LibertAI - Message: {message}")
            tool_choice = self.detect_tool_choice(message)
            print(f"🔍 DEBUG LibertAI - tool_choice: {tool_choice}")
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=500,
                    temperature=0.1,
                    tools=self.get_tools_schema(),
                    tool_choice=tool_choice
                )
                if not response or not hasattr(response, 'choices') or not response.choices:
                    print(f"❌ LibertAI response invalide: {response}")
                    return "❌ Erreur: LibertAI n'a pas retourné de réponse valide. Vérifiez votre clé API et votre connexion."
            except Exception as e:
                print(f"❌ Erreur lors de l'appel LibertAI: {e}")
                return f"❌ Erreur de communication avec LibertAI: {str(e)}"

            response_message = response.choices[0].message
            if response_message.tool_calls:
                tool_calls = response_message.tool_calls
                tool_results = []
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    print(f"🔧 LibertAI Tool Call: {tool_name} with args: {tool_args}")
                    if tool_name == "get_crypto_price":
                        result = get_crypto_price(tool_args.get("crypto_id", ""), tool_args.get("currency", "usd"))
                    elif tool_name == "request_transaction":
                        result = request_transaction(
                            tool_args.get("recipient_address", ""),
                            tool_args.get("amount", ""),
                            tool_args.get("currency", "ETH"),
                            tool_args.get("token_address")
                        )
                    elif tool_name == "get_lifi_tokens":
                        result = get_lifi_tokens(tool_args.get("chains"))
                    elif tool_name == "get_swap_quote":
                        result = get_swap_quote(
                            tool_args.get("from_token", ""),
                            tool_args.get("to_token", ""),
                            tool_args.get("amount", ""),
                            tool_args.get("from_address", ""),
                            tool_args.get("from_chain", "1"),
                            tool_args.get("to_chain", "1")
                        )
                    elif tool_name == "execute_swap":
                        result = execute_swap(
                            tool_args.get("from_token", ""),
                            tool_args.get("to_token", ""),
                            tool_args.get("amount", ""),
                            tool_args.get("from_address", ""),
                            tool_args.get("from_chain", "1"),
                            tool_args.get("to_chain", "1")
                        )
                    elif tool_name == "get_sepolia_tokens":
                        result = get_sepolia_tokens()
                    elif tool_name == "get_all_erc20_tokens":
                        result = get_all_erc20_tokens(tool_args.get("chain_id", "11155111"))
                    else:
                        result = f"❌ Unknown tool: {tool_name}"
                    tool_results.append(f"Tool {tool_name} result: {result}")

                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                    response_message,
                    {"role": "tool", "content": "\n".join(tool_results)}
                ]
                try:
                    second_response = await client.chat.completions.create(
                        model=model,
                        messages=messages,
                        max_tokens=300,
                        temperature=0.1
                    )
                    if not second_response or not hasattr(second_response, 'choices') or not second_response.choices:
                        print(f"❌ LibertAI second response invalide: {second_response}")
                        return "❌ Erreur: LibertAI n'a pas retourné de réponse finale valide."
                    final_response = second_response.choices[0].message.content
                    return final_response
                except Exception as e:
                    print(f"❌ Erreur lors du second appel LibertAI: {e}")
                    return f"❌ Erreur lors de la génération de la réponse finale: {str(e)}"

            direct_response = response_message.content
            return direct_response
        except Exception as e:
            return f"❌ Error in LibertAI chat: {str(e)}"

