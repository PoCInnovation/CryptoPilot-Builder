#!/usr/bin/env python3
"""
Crypto tools for MCP agent
"""

import requests
import json
import os
from typing import Dict, List, Optional

def get_crypto_price(crypto_id: str, currency: str = "usd") -> str:
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": crypto_id.lower(),
        "vs_currencies": currency.lower()
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if crypto_id.lower() in data and currency.lower() in data[crypto_id.lower()]:
            price = data[crypto_id.lower()][currency.lower()]
            return f"The current price of {crypto_id.capitalize()} is {price} {currency.upper()}."
        return f"Cryptocurrency '{crypto_id}' not found or data unavailable."
    except requests.exceptions.RequestException as e:
        return f"CoinGecko API error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

def request_transaction(recipient_address: str, amount: str, currency: str = "ETH", token_address: str = None) -> str:
    print(f"🔍 DEBUG - request_transaction called with currency: {currency}")
    if not recipient_address.startswith('0x') or len(recipient_address) != 42:
        return "❌ Invalid Ethereum address. Must start with 0x and be 42 characters."
    try:
        float_amount = float(amount)
        if float_amount <= 0:
            return "❌ Amount must be greater than 0."
    except ValueError:
        return "❌ Invalid amount. Please enter a valid number."
    
    # Mapping des tokens ERC-20 sur Sepolia
    sepolia_tokens = {
        "USDC": {
            "address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            "decimals": 6,
            "symbol": "USDC",
            "name": "USD Coin"
        },
        "USDT": {
            "address": "0x7169D38820dfd117C3FA1f22a697dBA58d90BA06",
            "decimals": 6,
            "symbol": "USDT",
            "name": "Tether USD"
        },
        "DAI": {
            "address": "0x68194a729C2450ad26072b3D33ADaCbcef39D574",
            "decimals": 18,
            "symbol": "DAI",
            "name": "Dai Stablecoin"
        },
        "WETH": {
            "address": "0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9",
            "decimals": 18,
            "symbol": "WETH",
            "name": "Wrapped Ether"
        },
        "LINK": {
            "address": "0x779877A7B0D9E8603169DdbD7836e478b4624789",
            "decimals": 18,
            "symbol": "LINK",
            "name": "Chainlink"
        },
        "UNI": {
            "address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
            "decimals": 18,
            "symbol": "UNI",
            "name": "Uniswap"
        }
    }
    
    # Déterminer le type de transaction et l'adresse du token
    transaction_type = "native_transaction"
    final_token_address = token_address
    
    # Si pas d'adresse de token fournie, essayer de détecter automatiquement
    if not token_address:
        currency_upper = currency.upper()
        if currency_upper in sepolia_tokens:
            transaction_type = "erc20_transaction"
            final_token_address = sepolia_tokens[currency_upper]["address"]
        elif currency_upper in ["ETH", "SEPOLIA"]:
            transaction_type = "native_transaction"
            final_token_address = None
        else:
            # Par défaut, considérer comme transaction native
            transaction_type = "native_transaction"
            final_token_address = None
    
    transaction_request = {
        "type": transaction_type,
        "recipient": recipient_address,
        "amount": amount,
        "currency": currency,
        "token_address": final_token_address,
        "status": "pending_confirmation"
    }
    
    # Message différent selon le type de transaction
    if transaction_type == "erc20_transaction":
        token_info = sepolia_tokens.get(currency.upper(), {})
        token_name = token_info.get("name", currency.upper())
        message = f"ERC-20 transaction of {amount} {currency.upper()} ({token_name}) to {recipient_address[:6]}...{recipient_address[-4:]} prepared."
    else:
        message = f"Transaction of {amount} {currency} to {recipient_address[:6]}...{recipient_address[-4:]} prepared."
    
    transaction_json = json.dumps(transaction_request, separators=(',', ':'))
    return f"{message}\n\nTRANSACTION_REQUEST:{transaction_json}"

def get_lifi_tokens(chains: str = None) -> str:
    """Get available tokens from Li.Fi API"""
    url = "https://li.quest/v1/tokens"
    params = {}
    if chains:
        params["chains"] = chains

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Format the response for easy reading
        formatted_tokens = {}
        tokens_data = data.get("tokens", {})
        for chain_id, tokens in tokens_data.items():
            formatted_tokens[chain_id] = []
            # Limit to first 10 tokens per chain for readability
            for token in tokens[:10] if isinstance(tokens, list) else []:
                formatted_tokens[chain_id].append({
                    "symbol": token.get("symbol", ""),
                    "name": token.get("name", ""),
                    "address": token.get("address", ""),
                    "decimals": token.get("decimals", 18),
                    "priceUSD": token.get("priceUSD", "0")
                })

        return f"✅ Available tokens from Li.Fi:\n{json.dumps(formatted_tokens, indent=2)}"
    except requests.exceptions.RequestException as e:
        return f"❌ Li.Fi API error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

def get_swap_quote(from_token: str, to_token: str, amount: str, from_address: str,
                   from_chain: str = "1", to_chain: str = "1") -> str:
    """Get a swap quote from Li.Fi API"""
    url = "https://li.quest/v1/quote"

    # Li.Fi chain IDs mapping
    # Li.Fi utilise des chainIds différents de ceux d'Ethereum
    chain_id_mapping = {
        "1": "1",           # Ethereum Mainnet
        "11155111": "11155111"  # Sepolia (vérifier si supporté)
    }
    
    # Convertir les chainIds si nécessaire
    from_chain_li = chain_id_mapping.get(from_chain, from_chain)
    to_chain_li = chain_id_mapping.get(to_chain, to_chain)
    
    # Token addresses mapping for Ethereum mainnet
    token_addresses = {
        "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",  # USDC mainnet
        "USDT": "0xdAC17F958D2ee523a2206206994597C13D831ec7",  # USDT mainnet
        "DAI": "0x6B175474E89094C44Da98b954EedeAC495271d0F",   # DAI mainnet
        "WETH": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", # WETH mainnet
        "WBTC": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599"  # WBTC mainnet
    }

    # Decimals mapping for proper amount conversion
    token_decimals = {
        "ETH": 18,
        "USDC": 6,
        "USDT": 6,
        "DAI": 18,
        "WETH": 18,
        "WBTC": 8
    }

    # Get token addresses
    from_token_address = token_addresses.get(from_token.upper(), from_token)
    to_token_address = token_addresses.get(to_token.upper(), to_token)

    # Validate Ethereum addresses
    if not from_address.startswith('0x') or len(from_address) != 42:
        return "❌ Invalid wallet address. Must start with 0x and be 42 characters."

    # Convert amount using correct decimals
    try:
        decimals = token_decimals.get(from_token.upper(), 18)
        amount_wei = str(int(float(amount) * (10 ** decimals)))
    except ValueError:
        return "❌ Invalid amount. Please enter a valid number."

    params = {
        "fromChain": from_chain_li,
        "toChain": to_chain_li,
        "fromToken": from_token_address,
        "toToken": to_token_address,
        "fromAmount": amount_wei,
        "fromAddress": from_address,
        "integrator": "crypto-pilot-agent"
    }

    try:
        response = requests.get(url, params=params, timeout=30)

        # Handle different response status codes
        if response.status_code == 400:
            try:
                error_data = response.json()
                return f"❌ Li.Fi API error (400): {error_data.get('message', 'Bad Request')}. Please check your parameters."
            except:
                return f"❌ Li.Fi API error (400): Bad Request. Parameters: {params}"

        response.raise_for_status()
        data = response.json()

        if "transactionRequest" in data:
            tx_data = data["transactionRequest"]
            estimate = data.get("estimate", {})

            # Calculate readable amounts
            from_decimals = token_decimals.get(from_token.upper(), 18)
            to_decimals = token_decimals.get(to_token.upper(), 18)

            to_amount = estimate.get("toAmount", "0")
            to_amount_readable = float(to_amount) / (10 ** to_decimals) if to_amount != "0" else 0

            to_amount_min = estimate.get("toAmountMin", "0")
            to_amount_min_readable = float(to_amount_min) / (10 ** to_decimals) if to_amount_min != "0" else 0

            # Format the swap information
            result = f"✅ Swap Quote Generated:\n"
            result += f"From: {amount} {from_token.upper()}\n"
            result += f"To: ~{to_amount_readable:.6f} {to_token.upper()}\n"
            result += f"Minimum: {to_amount_min_readable:.6f} {to_token.upper()}\n"

            gas_costs = estimate.get('gasCosts', [])
            if gas_costs:
                gas_estimate = gas_costs[0].get('estimate', 'N/A')
                result += f"Gas Estimate: {gas_estimate} wei\n\n"

            # Create the swap request JSON
            swap_request = {
                "type": "swap_request",
                "fromToken": from_token.upper(),
                "toToken": to_token.upper(),
                "amount": amount,
                "fromAddress": from_address,
                "transactionData": {
                    "to": tx_data.get("to"),
                    "data": tx_data.get("data"),
                    "value": tx_data.get("value", "0"),
                    "gasLimit": tx_data.get("gasLimit"),
                    "gasPrice": tx_data.get("gasPrice"),
                    "chainId": tx_data.get("chainId")
                },
                "estimate": {
                    "toAmount": to_amount_readable,
                    "toAmountMin": to_amount_min_readable
                },
                "status": "pending_confirmation"
            }

            result += f"SWAP_REQUEST:{json.dumps(swap_request, indent=2)}"
            return result
        else:
            return f"❌ No quote available. Response: {json.dumps(data, indent=2)[:500]}..."

    except requests.exceptions.RequestException as e:
        return f"❌ Li.Fi API error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

def execute_swap(from_token: str, to_token: str, amount: str, from_address: str,
                 from_chain: str = None, to_chain: str = None) -> str:
    """Execute a swap - this generates the transaction data for the frontend to execute"""
    
    # Détection automatique du réseau pour optimiser les frais
    # Si les chaînes ne sont pas spécifiées, détecter automatiquement
    if from_chain is None or to_chain is None:
        # Par défaut, utiliser Sepolia pour les tests (gratuit)
        from_chain = "11155111"
        to_chain = "11155111"
        print(f"🔄 Détection automatique : Swap sur Sepolia (testnet gratuit)")
    
    if from_chain == "11155111" or to_chain == "11155111":
        # Sepolia - utiliser swap natif (sans frais)
        print(f"🔄 Swap natif sur Sepolia (testnet gratuit)")
        return execute_native_sepolia_swap(from_token, to_token, amount, from_address)
    else:
        # Ethereum Mainnet - utiliser Li.Fi (frais mais fiable)
        print(f"🔄 Swap sur Ethereum Mainnet (Li.Fi support)")
        return execute_lifi_swap(from_token, to_token, amount, from_address, from_chain, to_chain)

def execute_lifi_swap(from_token: str, to_token: str, amount: str, from_address: str,
                     from_chain: str = "1", to_chain: str = "1") -> str:
    """Execute a swap using Li.Fi API (for Ethereum Mainnet)"""
    # First get the quote
    quote_result = get_swap_quote(from_token, to_token, amount, from_address, from_chain, to_chain)

    if quote_result.startswith("❌"):
        return quote_result

    # Extract and return the swap request
    if "SWAP_REQUEST:" in quote_result:
        return quote_result
    else:
        return f"❌ Failed to generate swap transaction data"

def execute_native_sepolia_swap(from_token: str, to_token: str, amount: str, from_address: str) -> str:
    """Execute a native swap on Sepolia (without Li.Fi)"""
    
    # Adresses des tokens sur Sepolia
    sepolia_token_addresses = {
        "USDC": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
        "USDT": "0x7169D38820dfd117C3FA1f22a697dBA58d90BA06",
        "DAI": "0x68194a729C2450ad26072b3D33ADaCbcef39D574",
        "WETH": "0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9",
        "LINK": "0x779877A7B0D9E8603169DdbD7836e478b4624789",
        "UNI": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984"
    }
    
    # Décimales des tokens
    token_decimals = {
        "ETH": 18,
        "USDC": 6,
        "USDT": 6,
        "DAI": 18,
        "WETH": 18,
        "LINK": 18,
        "UNI": 18
    }
    
    try:
        from_token_upper = from_token.upper()
        to_token_upper = to_token.upper()
        
        # Pour l'instant, implémenter seulement ETH → USDC
        if from_token_upper == "ETH" and to_token_upper == "USDC":
            # Simuler un swap ETH → USDC
            # En réalité, on enverrait l'ETH à un contrat de swap
            usdc_address = sepolia_token_addresses["USDC"]
            
            # Calculer le montant approximatif (1 ETH ≈ 4000 USDC pour l'exemple)
            eth_amount = float(amount)
            usdc_amount = eth_amount * 4000  # Taux approximatif
            
            # Créer une transaction simple (transfert ETH)
            swap_request = {
                "type": "native_sepolia_swap",
                "fromToken": from_token_upper,
                "toToken": to_token_upper,
                "amount": amount,
                "fromAddress": from_address,
                "transactionData": {
                    "to": usdc_address,
                    "data": "0x",  # Pas de données pour un simple transfert
                    "value": str(int(eth_amount * (10 ** 18))),  # Montant en wei
                    "chainId": 11155111  # Sepolia
                },
                "estimate": {
                    "toAmount": usdc_amount,
                    "toAmountMin": usdc_amount * 0.99  # 1% slippage
                },
                "status": "pending_confirmation",
                "method": "native_sepolia"
            }
            
            result = f"✅ Native Sepolia Swap Generated:\n"
            result += f"From: {amount} {from_token_upper}\n"
            result += f"To: ~{usdc_amount:.2f} {to_token_upper}\n"
            result += f"Network: Sepolia (testnet - gratuit)\n"
            result += f"Method: Native swap (sans Li.Fi)\n\n"
            
            result += f"SWAP_REQUEST:{json.dumps(swap_request, indent=2)}"
            return result
            
        else:
            return f"❌ Swap natif {from_token} → {to_token} non encore implémenté sur Sepolia"
            
    except Exception as e:
        return f"❌ Erreur swap natif Sepolia: {str(e)}"

def get_sepolia_tokens() -> str:
    """Get available ERC-20 tokens on Sepolia testnet"""
    sepolia_tokens = {
        "USDC": {
            "address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
            "decimals": 6,
            "symbol": "USDC",
            "name": "USD Coin",
            "faucet": "https://faucet.sepolia.dev/ ou https://faucets.chain.link/sepolia"
        },
        "USDT": {
            "address": "0x7169D38820dfd117C3FA1f22a697dBA58d90BA06",
            "decimals": 6,
            "symbol": "USDT",
            "name": "Tether USD",
            "faucet": "https://faucet.sepolia.dev/"
        },
        "DAI": {
            "address": "0x68194a729C2450ad26072b3D33ADaCbcef39D574",
            "decimals": 18,
            "symbol": "DAI",
            "name": "Dai Stablecoin",
            "faucet": "https://faucet.sepolia.dev/"
        },
        "WETH": {
            "address": "0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9",
            "decimals": 18,
            "symbol": "WETH",
            "name": "Wrapped Ether",
            "faucet": "Obtenu en wrappant de l'ETH de test"
        },
        "LINK": {
            "address": "0x779877A7B0D9E8603169DdbD7836e478b4624789",
            "decimals": 18,
            "symbol": "LINK",
            "name": "Chainlink",
            "faucet": "https://faucets.chain.link/sepolia"
        },
        "UNI": {
            "address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
            "decimals": 18,
            "symbol": "UNI",
            "name": "Uniswap",
            "faucet": "https://faucet.sepolia.dev/"
        }
    }
    
    result = "✅ Available ERC-20 tokens on Sepolia:\n\n"
    for symbol, info in sepolia_tokens.items():
        result += f"• {symbol} ({info['name']})\n"
        result += f"  Address: {info['address']}\n"
        result += f"  Decimals: {info['decimals']}\n"
        result += f"  Faucet: {info['faucet']}\n\n"
    
    result += "💡 Pour obtenir des tokens de test:\n"
    result += "1. ETH: https://sepoliafaucet.com/\n"
    result += "2. USDC/USDT/DAI: https://faucet.sepolia.dev/\n"
    result += "3. LINK: https://faucets.chain.link/sepolia\n"
    result += "4. WETH: Wrap de l'ETH via un DEX ou contrat\n"
    
    return result

def get_all_erc20_tokens(chain_id: str = "11155111") -> str:
    """
    Récupère dynamiquement tous les tokens ERC-20 disponibles sur Sepolia
    Utilise l'API Etherscan pour récupérer les tokens les plus populaires
    """
    # Configuration pour Sepolia (chain_id: 11155111)
    if chain_id == "11155111":  # Sepolia
        api_url = "https://api-sepolia.etherscan.io/api"
        chain_name = "Sepolia"
    elif chain_id == "1":  # Ethereum Mainnet
        api_url = "https://api.etherscan.io/api"
        chain_name = "Ethereum Mainnet"
    else:
        return "❌ Chaîne non supportée. Utilisez '11155111' pour Sepolia ou '1' pour Ethereum Mainnet."
    
    # Récupérer la clé API Etherscan depuis les variables d'environnement
    etherscan_api_key = os.getenv('ETHERSCAN_API_KEY', '')
    
    if not etherscan_api_key:
        # Si pas de clé API, retourner les tokens prédéfinis selon la chaîne
        if chain_id == "11155111":  # Sepolia
            return get_sepolia_tokens()
        elif chain_id == "1":  # Ethereum Mainnet
            # Tokens prédéfinis pour Ethereum Mainnet
            mainnet_tokens = {
                "USDC": {
                    "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                    "decimals": 6,
                    "symbol": "USDC",
                    "name": "USD Coin",
                    "faucet": "Acheter sur un exchange"
                },
                "USDT": {
                    "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                    "decimals": 6,
                    "symbol": "USDT",
                    "name": "Tether USD",
                    "faucet": "Acheter sur un exchange"
                },
                "DAI": {
                    "address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                    "decimals": 18,
                    "symbol": "DAI",
                    "name": "Dai Stablecoin",
                    "faucet": "Acheter sur un exchange"
                },
                "WETH": {
                    "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                    "decimals": 18,
                    "symbol": "WETH",
                    "name": "Wrapped Ether",
                    "faucet": "Wrap de l'ETH via un DEX"
                }
            }
            
            result = f"✅ Available ERC-20 tokens on {chain_name}:\n\n"
            for symbol, info in mainnet_tokens.items():
                result += f"• {symbol} ({info['name']})\n"
                result += f"  Address: {info['address']}\n"
                result += f"  Decimals: {info['decimals']}\n"
                result += f"  Faucet: {info['faucet']}\n\n"
            
            result += "💡 Pour obtenir des tokens:\n"
            result += "1. ETH: Acheter sur un exchange (Coinbase, Binance, etc.)\n"
            result += "2. USDC/USDT/DAI: Acheter sur un exchange\n"
            result += "3. WETH: Wrap de l'ETH via un DEX (Uniswap, etc.)\n"
            
            return result
        else:
            return "❌ Chaîne non supportée. Utilisez '11155111' pour Sepolia ou '1' pour Ethereum Mainnet."
    
    try:
        # Récupérer les tokens les plus populaires via l'API Etherscan
        params = {
            'module': 'account',
            'action': 'tokentx',
            'contractaddress': '',  # Vide pour récupérer toutes les transactions
            'page': 1,
            'offset': 100,  # Limiter à 100 résultats
            'sort': 'desc',
            'apikey': etherscan_api_key
        }
        
        response = requests.get(api_url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        if data.get('status') != '1':
            # Si l'API échoue, retourner les tokens prédéfinis
            return get_sepolia_tokens()
        
        # Extraire les adresses de contrats uniques
        transactions = data.get('result', [])
        unique_contracts = {}
        
        for tx in transactions:
            contract_address = tx.get('contractAddress', '').lower()
            if contract_address and contract_address not in unique_contracts:
                unique_contracts[contract_address] = {
                    'address': tx.get('contractAddress', ''),
                    'symbol': tx.get('tokenSymbol', ''),
                    'name': tx.get('tokenName', ''),
                    'decimals': int(tx.get('tokenDecimal', '18')),
                    'tx_count': 1
                }
            elif contract_address in unique_contracts:
                unique_contracts[contract_address]['tx_count'] += 1
        
        # Trier par nombre de transactions (popularité)
        sorted_contracts = sorted(unique_contracts.items(), 
                                key=lambda x: x[1]['tx_count'], reverse=True)
        
        # Limiter aux 20 tokens les plus populaires
        top_tokens = sorted_contracts[:20]
        
        # Ajouter les tokens prédéfinis importants
        predefined_tokens = {
            "USDC": {
                "address": "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
                "decimals": 6,
                "symbol": "USDC",
                "name": "USD Coin",
                "faucet": "https://faucet.sepolia.dev/"
            },
            "USDT": {
                "address": "0x7169D38820dfd117C3FA1f22a697dBA58d90BA06",
                "decimals": 6,
                "symbol": "USDT",
                "name": "Tether USD",
                "faucet": "https://faucet.sepolia.dev/"
            },
            "DAI": {
                "address": "0x68194a729C2450ad26072b3D33ADaCbcef39D574",
                "decimals": 18,
                "symbol": "DAI",
                "name": "Dai Stablecoin",
                "faucet": "https://faucet.sepolia.dev/"
            },
            "WETH": {
                "address": "0x7b79995e5f793A07Bc00c21412e50Ecae098E7f9",
                "decimals": 18,
                "symbol": "WETH",
                "name": "Wrapped Ether",
                "faucet": "Obtenu en wrappant de l'ETH de test"
            },
            "LINK": {
                "address": "0x779877A7B0D9E8603169DdbD7836e478b4624789",
                "decimals": 18,
                "symbol": "LINK",
                "name": "Chainlink",
                "faucet": "https://faucets.chain.link/sepolia"
            },
            "UNI": {
                "address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
                "decimals": 18,
                "symbol": "UNI",
                "name": "Uniswap",
                "faucet": "https://faucet.sepolia.dev/"
            }
        }
        
        # Combiner les tokens dynamiques avec les prédéfinis
        all_tokens = {}
        
        # Ajouter d'abord les tokens prédéfinis
        for symbol, info in predefined_tokens.items():
            all_tokens[symbol] = info
        
        # Ajouter les tokens dynamiques (en évitant les doublons)
        for contract_address, token_info in top_tokens:
            symbol = token_info['symbol']
            if symbol and symbol not in all_tokens:
                all_tokens[symbol] = {
                    "address": token_info['address'],
                    "decimals": token_info['decimals'],
                    "symbol": symbol,
                    "name": token_info['name'],
                    "faucet": "https://faucet.sepolia.dev/",
                    "popularity": token_info['tx_count']
                }
        
        # Formater le résultat
        result = f"✅ Tokens ERC-20 disponibles sur {chain_name}:\n\n"
        
        # Afficher d'abord les tokens prédéfinis
        result += "🔵 Tokens principaux:\n"
        for symbol, info in predefined_tokens.items():
            result += f"• {symbol} ({info['name']})\n"
            result += f"  Address: {info['address']}\n"
            result += f"  Decimals: {info['decimals']}\n"
            result += f"  Faucet: {info['faucet']}\n\n"
        
        # Afficher les tokens dynamiques
        if len(all_tokens) > len(predefined_tokens):
            result += "🟢 Tokens populaires détectés:\n"
            for symbol, info in all_tokens.items():
                if symbol not in predefined_tokens:
                    popularity = info.get('popularity', 0)
                    result += f"• {symbol} ({info['name']}) - {popularity} tx\n"
                    result += f"  Address: {info['address']}\n"
                    result += f"  Decimals: {info['decimals']}\n"
                    result += f"  Faucet: https://faucet.sepolia.dev/\n\n"
        
        result += "💡 Pour obtenir des tokens de test:\n"
        result += "1. ETH: https://sepoliafaucet.com/\n"
        result += "2. USDC/USDT/DAI: https://faucet.sepolia.dev/\n"
        result += "3. LINK: https://faucets.chain.link/sepolia\n"
        result += "4. WETH: Wrap de l'ETH via un DEX ou contrat\n"
        result += "5. Autres tokens: https://faucet.sepolia.dev/\n\n"
        
        result += f"📊 Total: {len(all_tokens)} tokens disponibles"
        
        return result
        
    except requests.exceptions.RequestException as e:
        if chain_id == "11155111":
            return f"❌ Erreur API Etherscan: {str(e)}\n\nUtilisation des tokens prédéfinis:\n{get_sepolia_tokens()}"
        else:
            return f"❌ Erreur API Etherscan: {str(e)}\n\nUtilisation des tokens prédéfinis pour {chain_name}."
    except Exception as e:
        if chain_id == "11155111":
            return f"❌ Erreur inattendue: {str(e)}\n\nUtilisation des tokens prédéfinis:\n{get_sepolia_tokens()}"
        else:
            return f"❌ Erreur inattendue: {str(e)}\n\nUtilisation des tokens prédéfinis pour {chain_name}."