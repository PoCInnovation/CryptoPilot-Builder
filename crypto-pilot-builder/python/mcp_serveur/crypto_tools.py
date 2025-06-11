#!/usr/bin/env python3
"""
Crypto tools for MCP agent
"""

import requests

def get_crypto_price(crypto_id: str, currency: str = "usd") -> str:
    """
    Get real-time cryptocurrency price via CoinGecko API.

    Args:
        crypto_id: Cryptocurrency identifier (e.g. bitcoin, ethereum)
        currency: Desired currency (e.g. eur, usd, gbp). Default: usd

    Returns:
        str: Formatted message with price or error
    """
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
