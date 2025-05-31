from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from textwrap import dedent
import os
import logging
import json
import uuid

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from tools.test_tool import get_crypto_price
from tools.transaction_tool import request_transaction

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

sessions = {}

def create_agent_with_history(conversation_history=""):
    """Crée un agent avec l'historique de conversation intégré"""
    comportement = f"""
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

    HISTORIQUE DE LA CONVERSATION PRÉCÉDENTE :
    {conversation_history}
    Continue cette conversation en gardant le contexte de ce qui a été dit précédemment.
    """
    return Agent(
        model=OpenAIChat(id="gpt-4o-mini"),
        instructions=dedent(comportement),
        markdown=False,
        tools=[get_crypto_price, request_transaction],
    )

def format_conversation_history(messages):
    """Formate l'historique de conversation pour l'agent"""
    history = ""
    for msg in messages:
        if msg['role'] == 'user':
            history += f"Utilisateur: {msg['content']}\n"
        elif msg['role'] == 'assistant':
            history += f"Assistant: {msg['content']}\n"
        elif msg['role'] == 'system':
            history += f"Système: {msg['content']}\n"
    return history

@app.route('/new-session', methods=['POST'])
def create_new_session():
    """Crée une nouvelle session de chat"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        'messages': [],
        'conversation_history': ""
    }
    logger.info(f"Nouvelle session créée : {session_id}")
    return jsonify({'session_id': session_id})

@app.route('/chat', methods=['POST'])
def chat():
    logger.info("Requête POST reçue sur /chat")
    data = request.get_json()
    if not data or 'message' not in data:
        logger.warning("Aucun message fourni")
        return jsonify({'error': 'Message manquant'}), 400
    user_input = data['message']
    session_id = data.get('session_id')
    logger.info(f"Message utilisateur : {user_input}")
    logger.info(f"Session ID : {session_id}")
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {
            'messages': [],
            'conversation_history': ""
        }
        logger.info(f"Nouvelle session automatique créée : {session_id}")
    try:
        session_data = sessions[session_id]
        session_data['messages'].append({'role': 'user', 'content': user_input})
        conversation_history = format_conversation_history(session_data['messages'][:-1])
        agent = create_agent_with_history(conversation_history)
        logger.info("Envoi du message à l'agent avec contexte complet")
        logger.info(f"Historique de conversation: {conversation_history}")
        result = agent.run(user_input)
        logger.info("Réponse de l'agent reçue")
        if hasattr(result, 'content') and result.content:
            clean_response = result.content
        else:
            if hasattr(result, 'messages') and result.messages:
                for msg in reversed(result.messages):
                    if hasattr(msg, 'role') and msg.role == 'assistant' and hasattr(msg, 'content') and msg.content:
                        clean_response = msg.content
                        break
                else:
                    clean_response = str(result)
            else:
                clean_response = str(result)
        session_data['messages'].append({'role': 'assistant', 'content': clean_response})
        session_data['conversation_history'] = format_conversation_history(session_data['messages'])
        if "TRANSACTION_REQUEST:" in clean_response:
            try:
                parts = clean_response.split("TRANSACTION_REQUEST:")
                message_part = parts[0].strip()
                transaction_data = json.loads(parts[1])
                logger.info(f"Transaction détectée : {transaction_data}")
                return jsonify({
                    'response': message_part if message_part else f"Je vais préparer une transaction de {transaction_data['amount']} {transaction_data['currency']} vers {transaction_data['recipient']}. Confirmez-vous cette transaction ?",
                    'transaction_request': transaction_data,
                    'session_id': session_id
                })
            except (json.JSONDecodeError, IndexError) as e:
                logger.error(f"Erreur parsing transaction : {e}")
                return jsonify({
                    'response': clean_response,
                    'session_id': session_id
                })
        logger.info(f"Réponse nettoyée prête à être envoyée")
        logger.info(f"Nombre de messages dans la session: {len(session_data['messages'])}")
        return jsonify({
            'response': clean_response,
            'session_id': session_id
        })
    except Exception as e:
        logger.exception("Erreur lors de l'exécution de l'agent")
        return jsonify({
            'response': f"Erreur serveur : {str(e)}",
            'session_id': session_id
        }), 500

@app.route('/confirm-transaction', methods=['POST'])
def confirm_transaction():
    """Endpoint pour confirmer une transaction"""
    logger.info("Requête de confirmation de transaction reçue")
    data = request.get_json()
    if not data or 'confirmed' not in data:
        return jsonify({'error': 'Paramètre de confirmation manquant'}), 400
    session_id = data.get('session_id')
    if data['confirmed']:
        response_msg = 'Transaction confirmée par l\'utilisateur'
        logger.info(f"Transaction confirmée pour session {session_id}")
    else:
        response_msg = 'Transaction annulée par l\'utilisateur'
        logger.info(f"Transaction annulée pour session {session_id}")
    if session_id and session_id in sessions:
        sessions[session_id]['messages'].append({
            'role': 'system', 
            'content': response_msg
        })
        sessions[session_id]['conversation_history'] = format_conversation_history(sessions[session_id]['messages'])
    return jsonify({
        'status': 'confirmed' if data['confirmed'] else 'cancelled', 
        'message': response_msg,
        'session_id': session_id
    })

@app.route('/get-session-history', methods=['POST'])
def get_session_history():
    """Récupère l'historique d'une session"""
    data = request.get_json()
    session_id = data.get('session_id')
    if not session_id or session_id not in sessions:
        return jsonify({'error': 'Session non trouvée'}), 404
    return jsonify({
        'messages': sessions[session_id]['messages'],
        'conversation_history': sessions[session_id]['conversation_history'],
        'session_id': session_id
    })

@app.route('/delete-session', methods=['POST'])
def delete_session():
    """Supprime une session"""
    data = request.get_json()
    session_id = data.get('session_id')
    if session_id and session_id in sessions:
        del sessions[session_id]
        logger.info(f"Session supprimée : {session_id}")
        return jsonify({'status': 'deleted'})
    return jsonify({'error': 'Session non trouvée'}), 404

@app.route('/sessions', methods=['GET'])
def list_sessions():
    """Liste toutes les sessions actives"""
    session_list = []
    for session_id, data in sessions.items():
        session_list.append({
            'session_id': session_id,
            'message_count': len(data['messages']),
            'last_message': data['messages'][-1]['content'] if data['messages'] else None
        })
    return jsonify({'sessions': session_list})

if __name__ == "__main__":
    logger.info("Lancement du serveur Flask...")
    app.run(debug=True, host="0.0.0.0", port=5000)