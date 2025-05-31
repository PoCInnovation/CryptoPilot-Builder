from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from textwrap import dedent
import os
import logging
import json

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from tools.test_tool import get_crypto_price
from tools.transaction_tool import request_transaction

# Chargement des variables d'environnement
load_dotenv()

# Configuration des logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Création de l'app Flask
app = Flask(__name__)
CORS(app)

@app.route('/chat', methods=['POST'])
def chat():
    logger.info("Requête POST reçue sur /chat")
    data = request.get_json()
    if not data or 'message' not in data:
        logger.warning("Aucun message fourni")
        return jsonify({'error': 'Message manquant'}), 400
    
    user_input = data['message']
    logger.info(f"Message utilisateur : {user_input}")
    
    comportement = """
    Tu es un expert financier qui répond de manière claire, structurée et pédagogique aux questions sur la bourse.
    Tu peux expliquer le fonctionnement des actions, indices, ETF, crypto, ou tout autre instrument financier.

    Sois rigoureux, neutre et didactique. Utilise des exemples concrets si cela peut aider à comprendre.
    Si tu ne peux pas accéder à des données temps réel, précise-le.
    Si la question est trop vague, pose une question de clarification.

    Tu peux utiliser l'outil get_crypto_price pour obtenir le prix des cryptomonnaies.
    Tu peux aussi utiliser l'outil request_transaction pour initier des transactions blockchain.

    IMPORTANT pour les transactions :
    - Si l'utilisateur demande d'envoyer de la crypto (ex: "envoie 0.001 sepolia à 0x..."), utilise l'outil request_transaction
    - Sois très précis sur les montants et adresses
    - Explique toujours ce que tu vas faire avant de le faire
    - Les transactions nécessitent une confirmation de l'utilisateur

    Soit transparent avec les utilisateurs.
    """
    
    try:
        agent = Agent(
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=dedent(comportement),
            markdown=False,
            tools=[get_crypto_price, request_transaction],
        )
        logger.info("Agent initialisé avec succès")
        result = agent.run(user_input)
        logger.info("Réponse de l'agent reçue")
        
        if hasattr(result, 'content') and result.content:
            clean_response = result.content
        else:
            if hasattr(result, 'messages') and result.messages:
                for msg in reversed(result.messages):
                    if msg.role == 'assistant' and msg.content:
                        clean_response = msg.content
                        break
                else:
                    clean_response = str(result)
            else:
                clean_response = str(result)
        if "TRANSACTION_REQUEST:" in clean_response:
            try:
                parts = clean_response.split("TRANSACTION_REQUEST:")
                message_part = parts[0].strip()
                transaction_data = json.loads(parts[1])
                logger.info(f"Transaction détectée : {transaction_data}")
                return jsonify({
                    'response': message_part if message_part else f"Je vais préparer une transaction de {transaction_data['amount']} {transaction_data['currency']} vers {transaction_data['recipient']}. Confirmez-vous cette transaction ?",
                    'transaction_request': transaction_data
                })
            except (json.JSONDecodeError, IndexError) as e:
                logger.error(f"Erreur parsing transaction : {e}")
                return jsonify({'response': clean_response})
        logger.info(f"Réponse nettoyée prête à être envoyée")
        return jsonify({'response': clean_response})
    except Exception as e:
        logger.exception("Erreur lors de l'exécution de l'agent")
        return jsonify({'response': f"Erreur serveur : {str(e)}"}), 500

@app.route('/confirm-transaction', methods=['POST'])
def confirm_transaction():
    """Endpoint pour confirmer une transaction"""
    logger.info("Requête de confirmation de transaction reçue")
    data = request.get_json()
    
    if not data or 'confirmed' not in data:
        return jsonify({'error': 'Paramètre de confirmation manquant'}), 400
    
    if data['confirmed']:
        return jsonify({'status': 'confirmed', 'message': 'Transaction confirmée par l\'utilisateur'})
    else:
        return jsonify({'status': 'cancelled', 'message': 'Transaction annulée par l\'utilisateur'})

if __name__ == "__main__":
    logger.info("Lancement du serveur Flask...")
    app.run(debug=True, host="0.0.0.0", port=5000)