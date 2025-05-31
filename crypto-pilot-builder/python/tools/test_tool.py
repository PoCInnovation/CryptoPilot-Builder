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

@tool
def detect_transaction_intent(prompt: str) -> dict:
    """
    Détecte si l'utilisateur souhaite effectuer une transaction Ethereum.
    Retourne un dictionnaire avec les détails si une intention est détectée.
    """
    prompt_lower = prompt.lower()
    keywords = ["envoyer", "transfer", "transférer", "envoie", "envois"]
    if any(word in prompt_lower for word in keywords):
        # Extraction basique de l'adresse et du montant (à améliorer avec NLP)
        import re
        address_match = re.search(r'0x[a-fA-F0-9]{40}', prompt)
        eth_match = re.search(r'(\d+\.?\d*)\s*(eth|ether|ETH)', prompt)
        return {
            "intent": "transaction",
            "address": address_match.group(0) if address_match else None,
            "amount": eth_match.group(1) if eth_match else None
        }
    return {"intent": "none"}

@tool
def confirm_transaction(details: dict) -> str:
    """
    Outil pour demander confirmation à l'utilisateur avant d'exécuter une transaction.
    """
    if not details.get("address") or not details.get("amount"):
        return "Je n'ai pas pu extraire tous les détails de la transaction."
    return f"""
    Je vais envoyer {details['amount']} ETH à l'adresse :
    {details['address']}
    Confirmez-vous cette transaction ? Répondez par "oui" ou "non".
    """

# Test de l'outil
if __name__ == "__main__":
    print(get_crypto_price("bitcoin", "usd"))
    print(get_crypto_price("ethereum", "gbp"))