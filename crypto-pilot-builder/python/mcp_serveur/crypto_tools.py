#!/usr/bin/env python3
"""
Crypto tools for MCP agent
"""

import requests

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