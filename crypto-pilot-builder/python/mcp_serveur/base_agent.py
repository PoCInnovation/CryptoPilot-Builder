#!/usr/bin/env python3
"""
Base interface and shared utilities for all AI agents.

This module centralizes common logic used by different providers
(e.g., OpenAI, LibertAI) to avoid duplication:
- Default system prompt rules
- Tool schemas
- Intent detection for forcing tool_choice
- Prompt/context composition helpers
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

import json

class BaseAgent(ABC):
    """Base class for all AI agents with crypto capabilities"""

    @abstractmethod
    async def process_message(self, message: str, context: str = "") -> str:
        """Process a message with default configuration"""
        pass

    @abstractmethod
    async def process_message_with_config(self, message: str, context: str = "",
        system_prompt: str = "", model: str = "",
        api_key: str = "", modules: dict = None) -> str:
        """Process a message with custom configuration"""
        pass

    # ===== Shared utilities to reduce duplication between providers =====
    def get_shared_system_prompt(self) -> str:
        """Return the shared system prompt containing core crypto rules.

        Providers can prefix/suffix this if needed, but the rules remain identical.
        """
        return (
            "You are a crypto assistant with advanced capabilities including:\n"
            "1. **Price Information**: Get real-time cryptocurrency prices using get_crypto_price\n"
            "2. **Transactions**: Prepare blockchain transactions using request_transaction\n"
            "3. **Token Information**: Get available ERC-20 tokens on Sepolia using get_sepolia_tokens\n"
            "4. **Token Swapping**: Complete token swap capabilities using Li.Fi:\n"
            "   - get_lifi_tokens: Discover available tokens for swapping\n"
            "   - get_swap_quote: Get quotes for token swaps\n"
            "   - execute_swap: Execute token swaps with transaction data\n\n"
            "🎯 RÈGLE CRITIQUE pour request_transaction :\n\n"
            "COPIE EXACTEMENT le mot que dit l'utilisateur dans le paramètre \"currency\". NE TRADUIS PAS, NE CONVERTIS PAS.\n\n"
            "EXEMPLES CORRECTS :\n"
            "- User: \"envoie 0.001 ETH à 0x123...\" → request_transaction(..., currency=\"ETH\")\n"
            "- User: \"envoie 0.001 sepolia à 0x123...\" → request_transaction(..., currency=\"sepolia\")\n"
            "- User: \"envoie 5 USDC à 0x123...\" → request_transaction(..., currency=\"USDC\")\n\n"
            "❌ ERREUR FATALE (ne jamais faire) :\n"
            "- User dit \"ETH\" mais tu mets currency=\"sepolia\" ← INTERDIT !\n\n"
            "✅ TOKENS DISPONIBLES : ETH, SEPOLIA, USDC, USDT, DAI, WETH, LINK, UNI\n\n"
            "RÈGLES CRITIQUES pour les swaps :\n"
            "1. DÉTECTION : Si tu détectes l'un de ces mots-clés dans le message :\n"
            "   - \"swap\", \"échanger\", \"convertir\", \"changer\", \"exchange\"\n"
            "   - OU phrases comme \"eth en usdc\", \"bitcoin vers dai\", \"0.001 eth en usdc\"\n"
            "   - OU demandes directes de swap avec montant\n"
            "2. EXTRACTION : Extrais ces informations du message :\n"
            "   - Le token source (ex: ETH, USDC, BTC)\n"
            "   - Le token destination (ex: USDC, DAI, WETH)\n"
            "   - Le montant numérique\n"
            "3. ACTION IMMÉDIATE : Utilise DIRECTEMENT l'outil execute_swap avec ces paramètres.\n"
            "   - Pour ETH → USDC : execute_swap(\"ETH\", \"USDC\", montant, adresse_wallet)\n"
            "   - Pour USDC → DAI : execute_swap(\"USDC\", \"DAI\", montant, adresse_wallet)\n"
            "   - Si pas d'adresse wallet, utilise une adresse par défaut ou demande à l'utilisateur\n\n"
            "IMPORTANT :\n"
            "- NE DONNE JAMAIS d'explication préalable sur le swap\n"
            "- N'INFORME PAS l'utilisateur des détails avant d'appeler l'outil\n"
            "- NE DEMANDE JAMAIS de confirmation comme \"Souhaitez-vous continuer ?\"\n"
            "- APPELLE execute_swap IMMÉDIATEMENT dès que tu détectes une demande de swap\n"
            "- La modal d'interface se charge de tout afficher à l'utilisateur\n\n"
            "Provide clear, helpful responses about crypto prices, transactions, and swaps."
        )

    def append_modules_and_context(self, system_prompt: str, context: str = "", modules: Optional[dict] = None) -> str:
        """Append modules and context information to the system prompt consistently."""
        if modules:
            active_modules = [name for name, active in modules.items() if active]
            if active_modules:
                system_prompt += f"\nModules activés: {', '.join(active_modules)}"
        if context:
            # Context may be plain text or JSON string from caller; keep as-is
            label = "Contexte de conversation" if any(c in system_prompt for c in ["RÈGLE", "DÉTECTION"]) else "Conversation context"
            system_prompt += f"\n{label}: {context}"
        return system_prompt

    def detect_tool_choice(self, message: str) -> Union[str, Dict[str, Any]]:
        """Detect if we should force a specific tool based on keywords, else return 'auto'."""
        lower_msg = message.lower()
        transaction_keywords = ["envoie", "envoyer", "send", "transfer", "transférer", "payment", "pay"]
        has_transaction_keyword = any(keyword in lower_msg for keyword in transaction_keywords)
        has_address = "0x" in message and len([part for part in message.split() if part.startswith("0x") and len(part) == 42]) > 0
        has_amount = any(char.isdigit() for char in message)
        is_likely_transaction = has_transaction_keyword and has_address and has_amount

        swap_keywords = ["swap", "échanger", "convertir", "changer", "exchange", "en usdc", "en dai", "vers usdc", "vers dai"]
        has_swap_keyword = any(keyword in lower_msg for keyword in swap_keywords)
        has_swap_amount = any(char.isdigit() for char in message)
        is_likely_swap = has_swap_keyword and has_swap_amount

        if is_likely_transaction:
            return {"type": "function", "function": {"name": "request_transaction"}}
        if is_likely_swap:
            return {"type": "function", "function": {"name": "execute_swap"}}
        return "auto"

    def get_tools_schema(self) -> List[Dict[str, Any]]:
        """Return the shared tools schema list used for chat.completions.create."""
        return [
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
                    "description": "Request a blockchain transaction",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "recipient_address": {"type": "string", "description": "Ethereum recipient address"},
                            "amount": {"type": "string", "description": "Amount to send"},
                            "currency": {"type": "string", "description": "EXACT word user said: If user says 'ETH' use 'ETH', if user says 'sepolia' use 'sepolia'. NEVER convert ETH to sepolia!"},
                            "token_address": {"type": "string", "description": "Token contract address (optional)"}
                        },
                        "required": ["recipient_address", "amount"]
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
                        "properties": {"chains": {"type": "string", "description": "Comma-separated chain IDs to filter tokens (optional)"}},
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
                            "from_token": {"type": "string", "description": "Source token symbol or address (e.g., ETH, USDC)"},
                            "to_token": {"type": "string", "description": "Destination token symbol or address (e.g., USDC, DAI)"},
                            "amount": {"type": "string", "description": "Amount to swap"},
                            "from_address": {"type": "string", "description": "User's wallet address"},
                            "from_chain": {"type": "string", "description": "Source blockchain ID (default: 1 for Ethereum)", "default": "1"},
                            "to_chain": {"type": "string", "description": "Destination blockchain ID (default: 1 for Ethereum)", "default": "1"}
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
                            "from_token": {"type": "string", "description": "Source token symbol or address (e.g., ETH, USDC)"},
                            "to_token": {"type": "string", "description": "Destination token symbol or address (e.g., USDC, DAI)"},
                            "amount": {"type": "string", "description": "Amount to swap"},
                            "from_address": {"type": "string", "description": "User's wallet address"},
                            "from_chain": {"type": "string", "description": "Source blockchain ID (default: 1 for Ethereum)", "default": "1"},
                            "to_chain": {"type": "string", "description": "Destination blockchain ID (default: 1 for Ethereum)", "default": "1"}
                        },
                        "required": ["from_token", "to_token", "amount", "from_address"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_sepolia_tokens",
                    "description": "Get available ERC-20 tokens on Sepolia testnet",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_all_erc20_tokens",
                    "description": "Get all ERC-20 tokens for a specific chain",
                    "parameters": {
                        "type": "object",
                        "properties": {"chain_id": {"type": "string", "description": "Chain ID (e.g., 1 for Ethereum, 11155111 for Sepolia)", "default": "11155111"}},
                        "required": []
                    }
                }
            }
        ]

