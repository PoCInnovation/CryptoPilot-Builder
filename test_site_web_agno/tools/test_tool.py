from agno.tools import tool
import requests

@tool
def get_crypto_price(crypto_id: str) -> str:
    """
    Outil pour obtenir les prix en temps réel des cryptomonnaies via CoinGecko.
    """
    print(f"[CoinGeckoTool] Recherche du prix pour : {crypto_id}")  # Log pour debug
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": crypto_id,
        "vs_currencies": "eur"
    }

    try:
        response = requests.get(url, params=params)
        print(f"[CoinGeckoTool] Code HTTP: {response.status_code}")  # Log HTTP
        response.raise_for_status()
        data = response.json()
        print(f"[CoinGeckoTool] Réponse JSON: {data}")  # Log contenu

        if crypto_id in data:
            price = data[crypto_id]["eur"]
            return f"Le prix actuel de {crypto_id} est {price} EUR."
        else:
            return f"Cryptomonnaie '{crypto_id}' introuvable."
    except requests.exceptions.RequestException as e:
        print(f"[CoinGeckoTool] Exception: {e}")  # Log erreur
        return f"Erreur lors de la récupération des données : {e}"

# Test de l'outil
if __name__ == "__main__":
    print(get_crypto_price("bitcoin"))