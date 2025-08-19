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
from crypto_tools import get_crypto_price, request_transaction, get_lifi_tokens, get_swap_quote, execute_swap, get_sepolia_tokens, get_all_erc20_tokens
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
                return None
        return self.default_client

    async def process_message(self, message: str, context: str = "") -> str:
        """Process message with default configuration"""
        try:
            client = self._get_default_client()
            if client is None:
                return "❌ Aucune clé API OpenAI configurée. Veuillez utiliser agent_chat_configured avec votre clé API."
            system_prompt = """You are a crypto assistant with advanced capabilities including:
1. **Price Information**: Get real-time cryptocurrency prices using get_crypto_price
2. **Transactions**: Prepare blockchain transactions using request_transaction
3. **Token Information**: Get available ERC-20 tokens on Sepolia using get_sepolia_tokens
4. **Token Swapping**: Complete token swap capabilities using Li.Fi:
   - get_lifi_tokens: Discover available tokens for swapping
   - get_swap_quote: Get quotes for token swaps
   - execute_swap: Execute token swaps with transaction data

🎯 RÈGLE CRITIQUE pour request_transaction :

COPIE EXACTEMENT le mot que dit l'utilisateur dans le paramètre "currency". NE TRADUIS PAS, NE CONVERTIS PAS.

EXEMPLES CORRECTS :
- User: "envoie 0.001 ETH à 0x123..." → request_transaction(..., currency="ETH")  
- User: "envoie 0.001 sepolia à 0x123..." → request_transaction(..., currency="sepolia")
- User: "envoie 5 USDC à 0x123..." → request_transaction(..., currency="USDC")

❌ ERREUR FATALE (ne jamais faire) :
- User dit "ETH" mais tu mets currency="sepolia" ← INTERDIT !

✅ TOKENS DISPONIBLES : ETH, SEPOLIA, USDC, USDT, DAI, WETH, LINK, UNI

RÈGLES CRITIQUES pour les swaps :
1. DÉTECTION : Si tu détectes l'un de ces mots-clés dans le message :
   - "swap", "échanger", "convertir", "changer", "exchange"
   - OU phrases comme "eth en usdc", "bitcoin vers dai", "0.001 eth en usdc"
   - OU demandes directes de swap avec montant
2. EXTRACTION : Extrais ces informations du message :
   - Le token source (ex: ETH, USDC, BTC)
   - Le token destination (ex: USDC, DAI, WETH)
   - Le montant numérique
3. ACTION IMMÉDIATE : Utilise DIRECTEMENT l'outil execute_swap avec ces paramètres.
   - Pour ETH → USDC : execute_swap("ETH", "USDC", montant, adresse_wallet)
   - Pour USDC → DAI : execute_swap("USDC", "DAI", montant, adresse_wallet)
   - Si pas d'adresse wallet, utilise une adresse par défaut ou demande à l'utilisateur

IMPORTANT :
- NE DONNE JAMAIS d'explication préalable sur le swap
- N'INFORME PAS l'utilisateur des détails avant d'appeler l'outil
- NE DEMANDE JAMAIS de confirmation comme "Souhaitez-vous continuer ?"
- APPELLE execute_swap IMMÉDIATEMENT dès que tu détectes une demande de swap
- La modal d'interface se charge de tout afficher à l'utilisateur

Provide clear, helpful responses about crypto prices, transactions, and swaps."""
            if context:
                system_prompt += f"\nConversation context: {context}"
            result = await self._chat_with_openai(message, system_prompt, self.model, client)
            return result
        except Exception as e:
            return f"❌ OpenAI agent error: {str(e)}"

    async def process_message_with_config(self, message: str, context: str = "",
                                        system_prompt: str = "", model: str = "gpt-4o-mini",
                                        api_key: str = "", modules: dict = None) -> str:
        """Process message with custom configuration"""
        try:
            client = self._get_default_client(api_key) if api_key else self._get_default_client()
            if not system_prompt:
                system_prompt = """You are a crypto assistant with advanced capabilities including:
1. **Price Information**: Get real-time cryptocurrency prices using get_crypto_price
2. **Transactions**: Prepare blockchain transactions using request_transaction
3. **Token Information**: Get available ERC-20 tokens on Sepolia using get_sepolia_tokens
4. **Token Swapping**: Complete token swap capabilities using Li.Fi:
   - get_lifi_tokens: Discover available tokens for swapping
   - get_swap_quote: Get quotes for token swaps
   - execute_swap: Execute token swaps with transaction data

🎯 RÈGLE CRITIQUE pour request_transaction :

COPIE EXACTEMENT le mot que dit l'utilisateur dans le paramètre "currency". NE TRADUIS PAS, NE CONVERTIS PAS.

EXEMPLES CORRECTS :
- User: "envoie 0.001 ETH à 0x123..." → request_transaction(..., currency="ETH")  
- User: "envoie 0.001 sepolia à 0x123..." → request_transaction(..., currency="sepolia")
- User: "envoie 5 USDC à 0x123..." → request_transaction(..., currency="USDC")

❌ ERREUR FATALE (ne jamais faire) :
- User dit "ETH" mais tu mets currency="sepolia" ← INTERDIT !

✅ TOKENS DISPONIBLES : ETH, SEPOLIA, USDC, USDT, DAI, WETH, LINK, UNI

RÈGLES CRITIQUES pour les swaps :
1. DÉTECTION : Si tu détectes l'un de ces mots-clés dans le message :
   - "swap", "échanger", "convertir", "changer", "exchange"
   - OU phrases comme "eth en usdc", "bitcoin vers dai", "0.001 eth en usdc"
   - OU demandes directes de swap avec montant
2. EXTRACTION : Extrais ces informations du message :
   - Le token source (ex: ETH, USDC, BTC)
   - Le token destination (ex: USDC, DAI, WETH)
   - Le montant numérique
3. ACTION IMMÉDIATE : Utilise DIRECTEMENT l'outil execute_swap avec ces paramètres.
   - Pour ETH → USDC : execute_swap("ETH", "USDC", montant, adresse_wallet)
   - Pour USDC → DAI : execute_swap("USDC", "DAI", montant, adresse_wallet)
   - Si pas d'adresse wallet, utilise une adresse par défaut ou demande à l'utilisateur

IMPORTANT :
- NE DONNE JAMAIS d'explication préalable sur le swap
- N'INFORME PAS l'utilisateur des détails avant d'appeler l'outil
- NE DEMANDE JAMAIS de confirmation comme "Souhaitez-vous continuer ?"
- APPELLE execute_swap IMMÉDIATEMENT dès que tu détectes une demande de swap
- La modal d'interface se charge de tout afficher à l'utilisateur

Provide clear, helpful responses about crypto prices, transactions, and swaps."""
            if modules:
                active_modules = [name for name, active in modules.items() if active]
                if active_modules:
                    system_prompt += f"\nModules activés: {', '.join(active_modules)}"
            if context:
                system_prompt += f"\nContexte de conversation: {context}"
            result = await self._chat_with_openai(message, system_prompt, model, client)
            return result
        except Exception as e:
            return f"❌ Erreur agent OpenAI avec configuration: {str(e)}"

    async def _chat_with_openai(self, message: str, system_prompt: str, model: str, client=None) -> str:
        """Handle chat with OpenAI including tool calls"""
        if client is None:
            client = self._get_default_client()
            if client is None:
                return "❌ OpenAI client not configured."
        try:
            # Détection des transactions
            transaction_keywords = ["envoie", "envoyer", "send", "transfer", "transférer", "payment", "pay"]
            has_transaction_keyword = any(keyword in message.lower() for keyword in transaction_keywords)
            has_address = "0x" in message and len([part for part in message.split() if part.startswith("0x") and len(part) == 42]) > 0
            has_amount = any(char.isdigit() for char in message)
            is_likely_transaction = has_transaction_keyword and has_address and has_amount
            
            # Détection des swaps
            swap_keywords = ["swap", "échanger", "convertir", "changer", "exchange", "en usdc", "en dai", "vers usdc", "vers dai"]
            has_swap_keyword = any(keyword in message.lower() for keyword in swap_keywords)
            has_swap_amount = any(char.isdigit() for char in message)
            is_likely_swap = has_swap_keyword and has_swap_amount
            
            # Debug logs
            print(f"🔍 DEBUG - Message: {message}")
            print(f"🔍 DEBUG - has_swap_keyword: {has_swap_keyword}")
            print(f"🔍 DEBUG - has_swap_amount: {has_swap_amount}")
            print(f"🔍 DEBUG - is_likely_swap: {is_likely_swap}")
            print(f"🔍 DEBUG - is_likely_transaction: {is_likely_transaction}")
            
            tool_choice = "auto"
            if is_likely_transaction:
                tool_choice = {"type": "function", "function": {"name": "request_transaction"}}
                print(f"🔍 DEBUG - Forcing request_transaction tool")
            elif is_likely_swap:
                tool_choice = {"type": "function", "function": {"name": "execute_swap"}}
                print(f"🔍 DEBUG - Forcing execute_swap tool")
            else:
                print(f"🔍 DEBUG - Using auto tool choice")
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
                            "name": "get_lifi_tokens",
                            "description": "Get available tokens from Li.Fi for swapping",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "chains": {
                                        "type": "string",
                                        "description": "Comma-separated chain IDs to filter tokens (optional)"
                                    }
                                },
                                "required": []
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_swap_quote",
                            "description": "Get a swap quote from Li.Fi API for token swapping",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "from_token": {
                                        "type": "string",
                                        "description": "Source token symbol or address (e.g., ETH, USDC)"
                                    },
                                    "to_token": {
                                        "type": "string",
                                        "description": "Destination token symbol or address (e.g., USDC, DAI)"
                                    },
                                    "amount": {
                                        "type": "string",
                                        "description": "Amount to swap"
                                    },
                                    "from_address": {
                                        "type": "string",
                                        "description": "User's wallet address"
                                    },
                                    "from_chain": {
                                        "type": "string",
                                        "description": "Source blockchain ID (default: 1 for Ethereum)",
                                        "default": "1"
                                    },
                                    "to_chain": {
                                        "type": "string",
                                        "description": "Destination blockchain ID (default: 1 for Ethereum)",
                                        "default": "1"
                                    }
                                },
                                "required": ["from_token", "to_token", "amount", "from_address"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "execute_swap",
                            "description": "Execute a crypto swap using Li.Fi - generates transaction data for user to sign",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "from_token": {
                                        "type": "string",
                                        "description": "Source token symbol or address (e.g., ETH, USDC)"
                                    },
                                    "to_token": {
                                        "type": "string",
                                        "description": "Destination token symbol or address (e.g., USDC, DAI)"
                                    },
                                    "amount": {
                                        "type": "string",
                                        "description": "Amount to swap"
                                    },
                                    "from_address": {
                                        "type": "string",
                                        "description": "User's wallet address"
                                    },
                                    "from_chain": {
                                        "type": "string",
                                        "description": "Source blockchain ID (default: 1 for Ethereum)",
                                        "default": "1"
                                    },
                                    "to_chain": {
                                        "type": "string",
                                        "description": "Destination blockchain ID (default: 1 for Ethereum)",
                                        "default": "1"
                                    }
                                },
                                "required": ["from_token", "to_token", "amount", "from_address"]
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
                        "description": "EXACT word user said: If user says 'ETH' use 'ETH', if user says 'sepolia' use 'sepolia', if user says 'USDC' use 'USDC'. NEVER convert ETH to sepolia!"
                    },
                                    "token_address": {
                                        "type": "string",
                                        "description": "ERC-20 token contract address (optional, for ERC-20 transactions)"
                                    }
                                },
                                "required": ["recipient_address", "amount"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_sepolia_tokens",
                            "description": "Get list of available ERC-20 tokens on Sepolia testnet with their addresses and decimals.",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_all_erc20_tokens",
                            "description": "Get all available ERC-20 tokens dynamically from blockchain (Sepolia or Ethereum Mainnet). Uses Etherscan API to discover popular tokens.",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "chain_id": {
                                        "type": "string",
                                        "description": "Chain ID: '11155111' for Sepolia, '1' for Ethereum Mainnet",
                                        "default": "11155111"
                                    }
                                },
                                "required": []
                            }
                        }
                    }
                ],
                tool_choice=tool_choice
            )
            response_message = response.choices[0].message
            if hasattr(response_message, "tool_calls") and response_message.tool_calls:
                print(f"🔍 DEBUG - Tool calls detected: {len(response_message.tool_calls)}")
                tool_responses = []
                for tool_call in response_message.tool_calls:
                    tool_name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    print(f"🔍 DEBUG - Tool called: {tool_name} with args: {args}")
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
                    elif tool_name == "request_transaction":
                        print(f"🔍 DEBUG - request_transaction called with args: {args}")
                        currency = args.get("currency", "ETH")
                        print(f"🔍 DEBUG - Currency extracted: {currency}")
                        
                        # SÉCURITÉ : Si l'IA met "sepolia" alors que l'utilisateur a dit "ETH", forcer "ETH"
                        # (Cette logique sera enlevée quand l'IA apprendra)
                        if currency.lower() == "sepolia":
                            print(f"⚠️ WARNING - IA a mis 'sepolia', mais on garde comme ça pour l'instant")
                        
                        result = request_transaction(
                            args.get("recipient_address", ""),
                            args.get("amount", ""),
                            currency,
                            args.get("token_address", None)
                        )
                        tool_responses.append({
                            "name": tool_name,
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                    elif tool_name == "get_lifi_tokens":
                        result = get_lifi_tokens(
                            args.get("chains", None)
                        )
                        tool_responses.append({
                            "name": tool_name,
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                    elif tool_name == "get_swap_quote":
                        result = get_swap_quote(
                            args.get("from_token", ""),
                            args.get("to_token", ""),
                            args.get("amount", ""),
                            args.get("from_address", ""),
                            args.get("from_chain", "1"),
                            args.get("to_chain", "1")
                        )
                        tool_responses.append({
                            "name": tool_name,
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                    elif tool_name == "get_sepolia_tokens":
                        result = get_sepolia_tokens()
                        tool_responses.append({
                            "name": tool_name,
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                    elif tool_name == "get_all_erc20_tokens":
                        chain_id = args.get("chain_id", "11155111")
                        result = get_all_erc20_tokens(chain_id)
                        tool_responses.append({
                            "name": tool_name,
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                    elif tool_name == "execute_swap":
                        print(f"🔍 DEBUG - execute_swap called with args: {args}")
                        result = execute_swap(
                            args.get("from_token", ""),
                            args.get("to_token", ""),
                            args.get("amount", ""),
                            args.get("from_address", ""),
                            args.get("from_chain", "11155111"),
                            args.get("to_chain", "11155111")
                        )
                        print(f"🔍 DEBUG - execute_swap result: {result}")
                        tool_responses.append({
                            "name": tool_name,
                            "content": result,
                            "tool_call_id": tool_call.id
                        })
                if tool_responses:
                    print(f"🔍 DEBUG - Tool responses: {[res['name'] for res in tool_responses]}")
                    for res in tool_responses:
                        if res["name"] == "request_transaction":
                            print(f"🔍 DEBUG - Returning request_transaction result directly")
                            return res["content"]
                        elif res["name"] == "execute_swap":
                            print(f"🔍 DEBUG - Returning execute_swap result directly")
                            return res["content"]
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
                    return final_response
            direct_response = response_message.content
            return direct_response
        except Exception as e:
            return f"❌ Error in chat: {str(e)}"

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
                        "description": "EXACT word user said: If user says 'ETH' use 'ETH', if user says 'sepolia' use 'sepolia'. NEVER convert ETH to sepolia!"
                    }
                },
                "required": ["recipient_address", "amount"]
            }
        ),
        Tool(
            name="get_lifi_tokens",
            description="Get available tokens from Li.Fi for swapping",
            inputSchema={
                "type": "object",
                "properties": {
                    "chains": {
                        "type": "string",
                        "description": "Comma-separated chain IDs to filter tokens (optional)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_swap_quote",
            description="Get a swap quote from Li.Fi API",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_token": {
                        "type": "string",
                        "description": "Source token symbol or address (e.g., ETH, USDC)"
                    },
                    "to_token": {
                        "type": "string",
                        "description": "Destination token symbol or address (e.g., USDC, DAI)"
                    },
                    "amount": {
                        "type": "string",
                        "description": "Amount to swap"
                    },
                    "from_address": {
                        "type": "string",
                        "description": "User's wallet address"
                    },
                    "from_chain": {
                        "type": "string",
                        "description": "Source blockchain ID (default: 1 for Ethereum)",
                        "default": "1"
                    },
                    "to_chain": {
                        "type": "string",
                        "description": "Destination blockchain ID (default: 1 for Ethereum)",
                        "default": "1"
                    }
                },
                "required": ["from_token", "to_token", "amount", "from_address"]
            }
        ),
        Tool(
            name="execute_swap",
            description="Execute a crypto swap using Li.Fi",
            inputSchema={
                "type": "object",
                "properties": {
                    "from_token": {
                        "type": "string",
                        "description": "Source token symbol or address (e.g., ETH, USDC)"
                    },
                    "to_token": {
                        "type": "string",
                        "description": "Destination token symbol or address (e.g., USDC, DAI)"
                    },
                    "amount": {
                        "type": "string",
                        "description": "Amount to swap"
                    },
                    "from_address": {
                        "type": "string",
                        "description": "User's wallet address"
                    },
                    "from_chain": {
                        "type": "string",
                        "description": "Source blockchain ID (default: 1 for Ethereum)",
                        "default": "1"
                    },
                    "to_chain": {
                        "type": "string",
                        "description": "Destination blockchain ID (default: 1 for Ethereum)",
                        "default": "1"
                    }
                },
                "required": ["from_token", "to_token", "amount", "from_address"]
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
        return [TextContent(type="text", text="❌ Invalid arguments")]
    if name == "get_crypto_price":
        crypto_id = arguments.get("crypto_id", "")
        currency = arguments.get("currency", "usd")
        if crypto_id:
            result = get_crypto_price(crypto_id, currency)
            return [TextContent(type="text", text=result)]
        return [TextContent(type="text", text="❌ crypto_id required")]
    if name == "request_transaction":
        recipient_address = arguments.get("recipient_address", "")
        amount = arguments.get("amount", "")
        currency = arguments.get("currency", "ETH")
        token_address = arguments.get("token_address", None)
        if recipient_address and amount:
            result = request_transaction(recipient_address, amount, currency, token_address)
            return [TextContent(type="text", text=result)]
        return [TextContent(type="text", text="❌ Missing required parameters: recipient_address, amount")]
    
    if name == "get_lifi_tokens":
        chains = arguments.get("chains", None)
        result = get_lifi_tokens(chains)
        return [TextContent(type="text", text=result)]

    if name == "get_sepolia_tokens":
        result = get_sepolia_tokens()
        return [TextContent(type="text", text=result)]

    if name == "get_all_erc20_tokens":
        chain_id = arguments.get("chain_id", "11155111")
        result = get_all_erc20_tokens(chain_id)
        return [TextContent(type="text", text=result)]

    if name == "get_swap_quote":
        from_token = arguments.get("from_token", "")
        to_token = arguments.get("to_token", "")
        amount = arguments.get("amount", "")
        from_address = arguments.get("from_address", "")
        from_chain = arguments.get("from_chain", "1")
        to_chain = arguments.get("to_chain", "1")

        if not all([from_token, to_token, amount, from_address]):
            return [TextContent(type="text", text="❌ Missing required parameters: from_token, to_token, amount, from_address")]

        result = get_swap_quote(from_token, to_token, amount, from_address, from_chain, to_chain)
        return [TextContent(type="text", text=result)]

    if name == "execute_swap":
        from_token = arguments.get("from_token", "")
        to_token = arguments.get("to_token", "")
        amount = arguments.get("amount", "")
        from_address = arguments.get("from_address", "")
        from_chain = arguments.get("from_chain", "1")
        to_chain = arguments.get("to_chain", "1")

        if not all([from_token, to_token, amount, from_address]):
            return [TextContent(type="text", text="❌ Missing required parameters: from_token, to_token, amount, from_address")]

        result = execute_swap(from_token, to_token, amount, from_address, from_chain or "11155111", to_chain or "11155111")
        return [TextContent(type="text", text=result)]

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
            return [TextContent(type="text", text="❌ Empty message")]
        result = await openai_agent.process_message_with_config(
            message=message,
            context=context,
            system_prompt=system_prompt,
            model=model,
            api_key=api_key,
            modules=modules
        )
        return [TextContent(type="text", text=result)]
    message = arguments.get("message", "")
    context = arguments.get("context", "")
    if not message:
        message = name if name and name != "agent_chat" else ""
    if not message:
        return [TextContent(type="text", text="❌ Empty message")]
    result = await openai_agent.process_message(message, context)
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
    asyncio.run(main())