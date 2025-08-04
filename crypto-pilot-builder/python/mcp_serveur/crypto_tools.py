#!/usr/bin/env python3
"""
Crypto tools for MCP agent
"""

import requests
import json
import time

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

def request_transaction(recipient_address: str, amount: str, currency: str = "sepolia") -> str:
    if not recipient_address.startswith('0x') or len(recipient_address) != 42:
        return "❌ Invalid Ethereum address. Must start with 0x and be 42 characters."
    try:
        float_amount = float(amount)
        if float_amount <= 0:
            return "❌ Amount must be greater than 0."
    except ValueError:
        return "❌ Invalid amount. Please enter a valid number."
    transaction_request = (
        f"TRANSACTION_REQUEST:{{"
        f"\"type\":\"transaction_request\","
        f"\"recipient\":\"{recipient_address}\","
        f"\"amount\":\"{amount}\","
        f"\"currency\":\"{currency}\","
        f"\"status\":\"pending_confirmation\""
        f"}}"
    )
    message = f"Transaction of {amount} {currency} to {recipient_address[:6]}...{recipient_address[-4:]} prepared."
    return f"{message}\n\n{transaction_request}"

def get_lifi_tokens(chains: str = None) -> str:
    """Get available tokens from Li.Fi API"""
    try:
        api_data = _get_lifi_tokens_data(chains or "1")
        tokens_data = api_data.get("tokens", {}) if isinstance(api_data, dict) else api_data

        # Format the response for easy reading
        formatted_tokens = {}
        for chain_id, tokens in tokens_data.items():
            formatted_tokens[chain_id] = []
            # Show more popular tokens (sorted by price USD)
            try:
                sorted_tokens = sorted(tokens, key=lambda x: float(x.get("priceUSD", "0") or "0"), reverse=True)
            except (ValueError, TypeError):
                sorted_tokens = tokens

            # Add ETH manually (native)
            if chain_id == "1":  # Ethereum mainnet
                formatted_tokens[chain_id].append({
                    "symbol": "ETH",
                    "name": "Ethereum",
                    "address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
                    "decimals": 18,
                    "priceUSD": "Native token"
                })

            # Limit to first 20 tokens per chain
            for token in sorted_tokens[:20] if isinstance(sorted_tokens, list) else []:
                price = token.get("priceUSD", "0")
                try:
                    price_float = float(price or "0")
                    include_token = price_float > 0.001
                except (ValueError, TypeError):
                    include_token = True

                if include_token:
                    formatted_tokens[chain_id].append({
                        "symbol": token.get("symbol", ""),
                        "name": token.get("name", ""),
                        "address": token.get("address", ""),
                        "decimals": token.get("decimals", 18),
                        "priceUSD": price
                    })

        result = f"✅ Available tokens from Li.Fi (top tokens by value):\n"
        for chain_id, tokens in formatted_tokens.items():
            result += f"\n🔗 Chain {chain_id}:\n"
            for token in tokens:
                symbol = token["symbol"]
                name = token["name"][:25] + "..." if len(token["name"]) > 25 else token["name"]
                price = token["priceUSD"]
                result += f"  • {symbol:8} - {name:28} - ${price}\n"

        return result
    except requests.exceptions.RequestException as e:
        return f"❌ Li.Fi API error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

# Global cache for Li.Fi tokens
_tokens_cache = {}
_cache_expiry = 0

def _get_lifi_tokens_data(chains: str = "1") -> dict:
    """Get tokens data from Li.Fi API with caching"""
    global _tokens_cache, _cache_expiry

    # Cache valid for 5 minutes
    if _tokens_cache and time.time() < _cache_expiry:
        return _tokens_cache

    url = "https://li.quest/v1/tokens"
    params = {"chains": chains} if chains else {}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        _tokens_cache = data
        _cache_expiry = time.time() + 300
        return data
    except Exception as e:
        # Fallback in case of API error
        if _tokens_cache:
            return _tokens_cache
        raise e

def _resolve_token_info(symbol: str, chain_id: str = "1") -> dict:
    """Resolve token symbol to address, decimals, etc. dynamically via LI.FI"""
    try:
        api_data = _get_lifi_tokens_data(chain_id)
        tokens_data = api_data.get("tokens", {}) if isinstance(api_data, dict) else api_data
        chain_tokens = tokens_data.get(chain_id, [])

        # Handle ETH as a special case (native token)
        if symbol.upper() == "ETH":
            return {
                "address": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",  # LI.FI native ETH address
                "decimals": 18,
                "symbol": "ETH",
                "name": "Ethereum",
                "priceUSD": "0"  # Price will be fetched separately if needed
            }

        # Search by symbol (case-insensitive)
        for token in chain_tokens:
            if token.get("symbol", "").upper() == symbol.upper():
                return {
                    "address": token.get("address"),
                    "decimals": token.get("decimals", 18),
                    "symbol": token.get("symbol"),
                    "name": token.get("name", ""),
                    "priceUSD": token.get("priceUSD", "0")
                }

        # Token not found
        print(f"Token '{symbol}' not found. Available tokens on chain {chain_id}: {[t.get('symbol', 'Unknown') for t in chain_tokens[:10]]}")
        return None

    except Exception as e:
        print(f"Error resolving token {symbol}: {e}")
        return None

def debug_token_resolution(symbol: str, chain_id: str = "1") -> str:
    """Debug function to test token resolution"""
    try:
        print(f"🔍 Debugging token resolution for '{symbol}' on chain {chain_id}")

        # Test cache and API data
        api_data = _get_lifi_tokens_data(chain_id)
        print(f"API data type: {type(api_data)}")
        print(f"API data keys: {list(api_data.keys()) if isinstance(api_data, dict) else 'Not a dict'}")

        tokens_data = api_data.get("tokens", {}) if isinstance(api_data, dict) else api_data
        print(f"Tokens data type: {type(tokens_data)}")
        print(f"Available chains: {list(tokens_data.keys()) if isinstance(tokens_data, dict) else 'Not a dict'}")

        chain_tokens = tokens_data.get(chain_id, [])
        print(f"Chain {chain_id} tokens count: {len(chain_tokens) if isinstance(chain_tokens, list) else 'Not a list'}")

        if isinstance(chain_tokens, list) and len(chain_tokens) > 0:
            print(f"First few tokens: {[t.get('symbol', 'No symbol') for t in chain_tokens[:5]]}")

        # Test resolution
        result = _resolve_token_info(symbol, chain_id)
        if result:
            return f"✅ Token resolved: {json.dumps(result, indent=2)}"
        else:
            return f"❌ Token '{symbol}' not found"

    except Exception as e:
        return f"❌ Debug error: {str(e)}"

def get_swap_quote(from_token: str, to_token: str, amount: str, from_address: str,
                   from_chain: str = "1", to_chain: str = "1") -> str:
    """Get a swap quote from Li.Fi API"""
    url = "https://li.quest/v1/quote"

    # Dynamic token resolution via LI.FI
    from_token_info = _resolve_token_info(from_token, from_chain)
    to_token_info = _resolve_token_info(to_token, to_chain)

    # Validate tokens
    if not from_token_info:
        return f"❌ Token '{from_token}' not found on chain {from_chain}. Use get_lifi_tokens to see available tokens."

    if not to_token_info:
        return f"❌ Token '{to_token}' not found on chain {to_chain}. Use get_lifi_tokens to see available tokens."

    # Validate Ethereum addresses
    if not from_address.startswith('0x') or len(from_address) != 42:
        return "❌ Invalid wallet address. Must start with 0x and be 42 characters."

    # Convert amount using correct decimals
    try:
        decimals = from_token_info["decimals"]
        amount_wei = str(int(float(amount) * (10 ** decimals)))
    except ValueError:
        return "❌ Invalid amount. Please enter a valid number."

    params = {
        "fromChain": from_chain,
        "toChain": to_chain,
        "fromToken": from_token_info["address"],
        "toToken": to_token_info["address"],
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
            from_decimals = from_token_info["decimals"]
            to_decimals = to_token_info["decimals"]

            to_amount = estimate.get("toAmount", "0")
            to_amount_readable = float(to_amount) / (10 ** to_decimals) if to_amount != "0" else 0

            to_amount_min = estimate.get("toAmountMin", "0")
            to_amount_min_readable = float(to_amount_min) / (10 ** to_decimals) if to_amount_min != "0" else 0

            # Format the swap information
            result = f"✅ Swap Quote Generated:\n"
            result += f"From: {amount} {from_token_info['symbol']} ({from_token_info['name']})\n"
            result += f"To: ~{to_amount_readable:.6f} {to_token_info['symbol']} ({to_token_info['name']})\n"
            result += f"Prix {from_token_info['symbol']}: ${from_token_info['priceUSD']}\n"
            result += f"Prix {to_token_info['symbol']}: ${to_token_info['priceUSD']}\n"
            result += f"Minimum: {to_amount_min_readable:.6f} {to_token_info['symbol']}\n"

            gas_costs = estimate.get('gasCosts', [])
            if gas_costs:
                gas_estimate = gas_costs[0].get('estimate', 'N/A')
                result += f"Gas Estimate: {gas_estimate} wei\n\n"

            # Create the swap request JSON
            swap_request = {
                "type": "swap_request",
                "fromToken": from_token_info["symbol"],
                "toToken": to_token_info["symbol"],
                "fromTokenInfo": from_token_info,
                "toTokenInfo": to_token_info,
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
                 from_chain: str = "1", to_chain: str = "1") -> str:
    """Execute a swap - this generates the transaction data for the frontend to execute"""
    # First get the quote
    quote_result = get_swap_quote(from_token, to_token, amount, from_address, from_chain, to_chain)

    if quote_result.startswith("❌"):
        return quote_result

    # Extract and return the swap request
    if "SWAP_REQUEST:" in quote_result:
        return quote_result
    else:
        return f"❌ Failed to generate swap transaction data"
