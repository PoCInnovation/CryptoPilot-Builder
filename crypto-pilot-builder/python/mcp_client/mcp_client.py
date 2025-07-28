#!/usr/bin/env python3
"""
MCP client for communication with OpenAI crypto agent
"""

import asyncio
import json
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

    async def chat_with_config(self, message: str, context: Dict[str, Any], api_key: str) -> Dict[str, Any]:
        """Communication with OpenAI agent using user configuration"""
        # Extraire la configuration de l'agent depuis le contexte
        agent_config = context.get('agent_config', {})

        # Construire le prompt système basé sur la configuration utilisateur ET la mémoire
        system_prompt = self._build_system_prompt(agent_config, context)

        # Préparer les arguments avec la configuration
        arguments = {
            "message": message,
            "context": json.dumps(context),
            "api_key": api_key,
            "model": agent_config.get('model', 'gpt-4o-mini'),
            "system_prompt": system_prompt,
            "modules": json.dumps(agent_config.get('modules', {}))
        }

        return await self.call_tool("agent_chat_configured", arguments)

    def _build_system_prompt(self, agent_config: Dict[str, Any], context: Dict[str, Any] = None) -> str:
        """Construire le prompt système basé sur la configuration de l'agent ET la mémoire utilisateur"""

        # Prompt de base
        base_prompt = agent_config.get('prompt', '')
        if not base_prompt:
            base_prompt = """Tu es un assistant IA spécialisé en cryptomonnaies. Tu es précis, utile et professionnel.

RÈGLES CRITIQUES pour les transactions :
1. DÉTECTION : Si tu détectes l'un de ces mots-clés dans le message :
   - "envoie", "envoyer", "send", "transfert", "transfer", "payer", "pay"
   - OU si tu vois une adresse Ethereum (0x...) avec un montant
2. EXTRACTION : Extrais ces informations du message :
   - L'adresse de destination (format 0x + 40 caractères)
   - Le montant numérique
   - La devise (par défaut "sepolia")
3. ACTION IMMÉDIATE : Utilise DIRECTEMENT l'outil request_transaction avec ces paramètres.

RÈGLES CRITIQUES pour les swaps :
1. DÉTECTION : Si tu détectes l'un de ces mots-clés dans le message :
   - "swap", "échanger", "convertir", "changer", "exchange"
   - OU phrases comme "eth en usdc", "bitcoin vers dai", "0.001 eth en usdc"
   - OU demandes directes de swap avec montant
2. EXTRACTION : Extrais ces informations du message :
   - Le token source (ex: ETH, USDC, BTC)
   - Le token destination (ex: USDC, DAI, WETH)
   - Le montant numérique
3. ACTION IMMÉDIATE : Utilise DIRECTEMENT l'outil execute_swap avec ces paramètres ET l'adresse du wallet connecté comme from_address.

EXEMPLES D'APPELS IMMÉDIATS :
- "0.001 eth en usdc" → APPELLE execute_swap("ETH", "USDC", "0.001", adresse_wallet)
- "swap 100 usdc vers dai" → APPELLE execute_swap("USDC", "DAI", "100", adresse_wallet)
- "échanger 0.5 eth" → APPELLE execute_swap("ETH", "USDC", "0.5", adresse_wallet) (USDC par défaut)

IMPORTANT :
- NE DONNE JAMAIS d'explication préalable sur le swap
- N'INFORME PAS l'utilisateur des détails avant d'appeler l'outil
- NE DEMANDE JAMAIS de confirmation comme "Souhaitez-vous continuer ?"
- APPELLE execute_swap IMMÉDIATEMENT dès que tu détectes une demande de swap
- La modal d'interface se charge de tout afficher à l'utilisateur

IMPORTANT : Dès que tu identifies une demande de transaction ou de swap, utilise l'outil IMMÉDIATEMENT sans autre discussion."""

        # NOUVELLE FONCTIONNALITÉ: Intégrer la mémoire utilisateur
        user_memory = ""
        if context and context.get('user_memory'):
            memory_text = context.get('user_memory', '').strip()
            if memory_text:
                user_memory = f"\n\n{memory_text}\n\nUtilise ces informations pour personnaliser tes réponses et maintenir une conversation cohérente avec l'utilisateur."

        # WALLET INFO: Integrate the connected wallet address
        wallet_info = ""
        if context and context.get('wallet_address'):
            wallet_address = context.get('wallet_address').strip()
            if wallet_address:
                wallet_info = f"\n\nADRESSE DU WALLET CONNECTÉ: {wallet_address}\n\nIMPORTANT: Quand tu utilises les outils de swap (get_swap_quote ou execute_swap), utilise TOUJOURS cette adresse comme from_address. Cette adresse représente le wallet de l'utilisateur connecté."

        # Ajouter les capacités des modules activés
        modules = agent_config.get('modules', {})
        module_capabilities = []

        if modules.get('chatAdvanced', False):
            module_capabilities.append("- Tu as une mémoire contextuelle avancée pour maintenir des conversations naturelles")

        if modules.get('dataAnalysis', False):
            module_capabilities.append("- Tu peux analyser et visualiser des données complexes")

        if modules.get('webSearch', False):
            module_capabilities.append("- Tu as accès aux informations en temps réel via la recherche web")

        if modules.get('creativeGeneration', False):
            module_capabilities.append("- Tu peux créer du contenu artistique et créatif")

        # Construire le prompt final
        system_prompt = base_prompt

        # Ajouter la mémoire utilisateur si disponible
        if user_memory:
            system_prompt += user_memory

        # Add wallet info if available
        if wallet_info:
            system_prompt += wallet_info

        # Ajouter les capacités des modules
        if module_capabilities:
            capabilities_text = "\n".join(module_capabilities)
            system_prompt += f"\n\nTes capacités spéciales incluent:\n{capabilities_text}"

        return system_prompt

    def is_connected(self) -> bool:
        """Check if client is configured"""
        return self.connected

# Global instance
mcp_client = MCPClient()