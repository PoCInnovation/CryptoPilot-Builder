from agno.tools import tool
import json

@tool
def request_transaction(recipient_address: str, amount: str, currency: str = "sepolia") -> str:
    """
    Outil pour demander une transaction blockchain depuis le chatbot.
    Args:
        recipient_address: L'adresse du destinataire (ex: 0x72FA462C75aE174416db42EE79277D4927EfFE92)
        amount: Le montant à envoyer (ex: 0.001)
        currency: La devise/réseau (par défaut: sepolia)
    """
    print(f"[TransactionTool] Demande de transaction : {amount} {currency} vers {recipient_address}")
    
    # Validation basique de l'adresse Ethereum
    if not recipient_address.startswith('0x') or len(recipient_address) != 42:
        return "❌ Adresse Ethereum invalide. L'adresse doit commencer par 0x et faire 42 caractères."
    
    try:
        float_amount = float(amount)
        if float_amount <= 0:
            return "❌ Le montant doit être supérieur à 0."
    except ValueError:
        return "❌ Montant invalide. Veuillez entrer un nombre valide."
    
    # Création de la demande de transaction
    transaction_request = {
        "type": "transaction_request",
        "recipient": recipient_address,
        "amount": amount,
        "currency": currency,
        "status": "pending_confirmation"
    }
    
    # Retourner une réponse structurée que le frontend peut intercepter
    return f"TRANSACTION_REQUEST:{json.dumps(transaction_request)}"