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
            return f"Le prix actuel de {crypto_id.capitalize()} est {price} {currency.upper()}."
        return f"Cryptomonnaie '{crypto_id}' introuvable ou données indisponibles."
        
    except requests.exceptions.RequestException as e:
        return f"Erreur API CoinGecko : {str(e)}"
    except Exception as e:
        return f"Erreur inattendue : {str(e)}"

@tool
def detect_transaction_intent(prompt: str) -> dict:
    """
    Détecte les intentions de transaction Ethereum avec amélioration NLP
    Retourne un dictionnaire avec les détails si une intention est détectée
    """
    prompt_lower = prompt.lower()
    transaction_keywords = ["envoyer", "transfer", "transférer", "envoie", "envois", "payer"]
    
    if any(word in prompt_lower for word in transaction_keywords):
        # Extraction améliorée avec regex et gestion des variantes
        import re
        address_match = re.search(r'(0x[a-fA-F0-9]{40}|[a-zA-Z0-9]{42})', prompt)
        eth_match = re.search(r'(\d+\.?\d*)\s*(eth|ether|ETH|Ethereum|ethereum|ETH.)', prompt)
        
        return {
            "intent": "transaction",
            "address": address_match.group(0) if address_match else None,
            "amount": eth_match.group(1) if eth_match else None,
            "currency": "eth" if eth_match else None
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