from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from textwrap import dedent
import os
import logging

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from tools.test_tool import get_crypto_price

# Chargement des variables d'environnement
load_dotenv()

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'app Flask
app = Flask(__name__)
CORS(app)

# Stockage des conversations par ID de chat (format texte simple)
conversation_history = {}

@app.route('/chat', methods=['POST'])
def chat():
    logger.info("Requête POST reçue sur /chat")
    data = request.get_json()
    if not data or 'message' not in data:
        logger.warning("Aucun message fourni")
        return jsonify({'error': 'Message manquant'}), 400

    # Récupérer l'ID du chat (utiliser 'default' s'il n'est pas fourni)
    chat_id = data.get('chat_id', 'default')
    user_input = data['message']
    logger.info(f"Message utilisateur pour le chat {chat_id}: {user_input}")

    # Initialiser l'historique pour ce chat s'il n'existe pas
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []

    # Stocker le message utilisateur en texte simple
    conversation_history[chat_id].append(user_input)

    comportement = """
    Tu es un expert financier qui repond de maniere claire, structuree et pedagogique aux questions sur la bourse.
    Tu peux expliquer le fonctionnement des actions, indices, ETF, crypto, ou tout autre instrument financier.

    Sois rigoureux, neutre et didactique. Utilise des exemples concrets si cela peut aider a comprendre.
    Si tu ne peux pas acceder a des donnees temps reel, precise-le.
    Si la question est trop vague, pose une question de clarification.

    Tu peux utiliser l'outil get_crypto_price pour obtenir le prix des cryptomonnaies.
    1. L'outil accepte deux parametres : crypto_id (comme 'bitcoin', 'ethereum') et currency (comme 'eur', 'usd', 'gbp').
    2. Si l'outil renvoie des donnees de prix valides, utilise ce prix exact dans ta reponse.
    3. Si l'outil signale une erreur (comme un depassement de quota), reconnait le probleme

    Soit transparent avec les utilisateurs.
    """

    # Créer un contexte avec l'historique des conversations
    context = ""
    if len(conversation_history[chat_id]) > 1:
        context = "Historique de conversation:\n"
        for i, msg in enumerate(conversation_history[chat_id][:-1]):
            if i % 2 == 0:  # Message utilisateur
                context += f"Utilisateur: {msg}\n"
            else:  # Message assistant
                context += f"Assistant: {msg}\n"
        context += "\nDernière question de l'utilisateur:\n"

    # Ajouter la dernière question
    full_prompt = context + user_input

    try:
        agent = Agent(
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=dedent(comportement),
            markdown=False,
            tools=[get_crypto_price],
        )
        logger.info("Agent initialisé avec succès")

        # Utiliser seulement le dernier message avec le contexte
        result = agent.run(full_prompt)
        logger.info("Réponse de l'agent reçue")

        if hasattr(result, 'content') and result.content:
            clean_response = result.content
        else:
            clean_response = str(result)

        # Stocker la réponse en texte simple
        conversation_history[chat_id].append(clean_response)

        logger.info(f"Réponse nettoyée prête à être envoyée")
        return jsonify({'response': clean_response})
    except Exception as e:
        logger.exception("Erreur lors de l'exécution de l'agent")
        return jsonify({'response': f"Erreur serveur : {str(e)}"}), 500

if __name__ == "__main__":
    logger.info("Lancement du serveur Flask...")
    app.run(debug=True, host="0.0.0.0", port=5000)