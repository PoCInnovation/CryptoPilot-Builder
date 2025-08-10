#!/usr/bin/env python3
"""
Crypto tools for MCP agent
"""

import requests
import json

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
        "fromChain": from_chain,
        "toChain": to_chain,
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