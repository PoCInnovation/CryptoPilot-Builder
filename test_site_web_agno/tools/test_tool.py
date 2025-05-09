from agno.tools import tool
import requests

@tool
def get_crypto_price(crypto_id: str, currency: str = "eur") -> str:
    """
    Outil pour obtenir les prix en temps réel des cryptomonnaies via CoinGecko.
    Args:
        crypto_id: L'identifiant de la cryptomonnaie (ex: bitcoin, ethereum)
        currency: La devise souhaitée (ex: eur, usd, gbp). Par défaut: eur
    """
    print(f"[CoinGeckoTool] Recherche du prix pour : {crypto_id} en {currency}")
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": crypto_id,
        "vs_currencies": currency
    }

    try:
        response = requests.get(url, params=params)
        print(f"[CoinGeckoTool] Code HTTP: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        print(f"[CoinGeckoTool] Réponse JSON: {data}")

        if crypto_id in data:
            price = data[crypto_id][currency]
            return f"Le prix actuel de {crypto_id} est {price} {currency.upper()}."
        else:
            return f"Cryptomonnaie '{crypto_id}' introuvable."
    except requests.exceptions.RequestException as e:
        print(f"[CoinGeckoTool] Exception: {e}")
        return f"Erreur lors de la récupération des données : {e}"

# Test de l'outil
if __name__ == "__main__":
    print(get_crypto_price("bitcoin", "usd"))
    print(get_crypto_price("ethereum", "gbp"))