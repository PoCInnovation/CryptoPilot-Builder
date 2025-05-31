from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from textwrap import dedent
import os
import logging
import json
import uuid
from datetime import datetime, timedelta

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

# Stockage des sessions de chat en mémoire
# En production, utilisez Redis, MongoDB ou une base de données
chat_sessions = {}

class ChatSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.agent = None
        self.messages = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialise l'agent avec le comportement défini"""
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
        Tu peux faire référence aux conversations précédentes dans cette session.
        """
        
        self.agent = Agent(
            model=OpenAIChat(id="gpt-4o-mini"),
            instructions=dedent(comportement),
            markdown=False,
            tools=[get_crypto_price, request_transaction],
        )
    
    def add_message(self, message, is_user=True):
        """Ajoute un message à l'historique"""
        self.messages.append({
            'content': message,
            'is_user': is_user,
            'timestamp': datetime.now().isoformat()
        })
        self.last_activity = datetime.now()
    
    def get_conversation_context(self):
        """Retourne le contexte de la conversation pour l'agent"""
        if not self.messages:
            return ""
        
        context = "Historique de la conversation:\n"
        for msg in self.messages[-10:]:  # Garde les 10 derniers messages
            role = "Utilisateur" if msg['is_user'] else "Assistant"
            context += f"{role}: {msg['content']}\n"
        return context

def cleanup_old_sessions():
    """Nettoie les sessions inactives (plus de 1 heure)"""
    current_time = datetime.now()
    expired_sessions = []
    
    for session_id, session in chat_sessions.items():
        if current_time - session.last_activity > timedelta(hours=1):
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        del chat_sessions[session_id]
        logger.info(f"Session expirée nettoyée: {session_id}")

def get_or_create_session(session_id=None):
    """Récupère ou crée une session de chat"""
    cleanup_old_sessions()
    
    if session_id and session_id in chat_sessions:
        session = chat_sessions[session_id]
        session.last_activity = datetime.now()
        return session
    
    # Créer une nouvelle session
    new_session_id = session_id or str(uuid.uuid4())
    new_session = ChatSession(new_session_id)
    chat_sessions[new_session_id] = new_session
    logger.info(f"Nouvelle session créée: {new_session_id}")
    return new_session

@app.route('/chat', methods=['POST'])
def chat():
    logger.info("Requête POST reçue sur /chat")
    data = request.get_json()
    if not data or 'message' not in data:
        logger.warning("Aucun message fourni")
        return jsonify({'error': 'Message manquant'}), 400
    
    user_input = data['message']
    session_id = data.get('session_id')  # ID de session optionnel du frontend
    
    logger.info(f"Message utilisateur : {user_input}")
    logger.info(f"Session ID : {session_id}")
    
    try:
        # Récupérer ou créer la session
        session = get_or_create_session(session_id)
        
        # Ajouter le message de l'utilisateur à l'historique
        session.add_message(user_input, is_user=True)
        
        # Préparer le contexte avec l'historique
        context = session.get_conversation_context()
        full_prompt = f"{context}\n\nUtilisateur: {user_input}"
        
        logger.info("Agent initialisé avec succès")
        
        # Utiliser l'agent de la session pour maintenir le contexte
        result = session.agent.run(full_prompt)
        logger.info("Réponse de l'agent reçue")
        
        # Extraire la réponse propre
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
        
        # Ajouter la réponse à l'historique
        session.add_message(clean_response, is_user=False)
        
        # Vérifier s'il y a une demande de transaction
        if "TRANSACTION_REQUEST:" in clean_response:
            try:
                parts = clean_response.split("TRANSACTION_REQUEST:")
                message_part = parts[0].strip()
                transaction_data = json.loads(parts[1])
                logger.info(f"Transaction détectée : {transaction_data}")
                return jsonify({
                    'response': message_part if message_part else f"Je vais préparer une transaction de {transaction_data['amount']} {transaction_data['currency']} vers {transaction_data['recipient']}. Confirmez-vous cette transaction ?",
                    'transaction_request': transaction_data,
                    'session_id': session.session_id
                })
            except (json.JSONDecodeError, IndexError) as e:
                logger.error(f"Erreur parsing transaction : {e}")
                return jsonify({
                    'response': clean_response,
                    'session_id': session.session_id
                })
        
        logger.info(f"Réponse nettoyée prête à être envoyée")
        return jsonify({
            'response': clean_response,
            'session_id': session.session_id
        })
        
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
    
    session_id = data.get('session_id')
    if session_id and session_id in chat_sessions:
        session = chat_sessions[session_id]
        if data['confirmed']:
            session.add_message("Transaction confirmée par l'utilisateur", is_user=False)
            return jsonify({
                'status': 'confirmed', 
                'message': 'Transaction confirmée par l\'utilisateur',
                'session_id': session_id
            })
        else:
            session.add_message("Transaction annulée par l'utilisateur", is_user=False)
            return jsonify({
                'status': 'cancelled', 
                'message': 'Transaction annulée par l\'utilisateur',
                'session_id': session_id
            })
    
    if data['confirmed']:
        return jsonify({'status': 'confirmed', 'message': 'Transaction confirmée par l\'utilisateur'})
    else:
        return jsonify({'status': 'cancelled', 'message': 'Transaction annulée par l\'utilisateur'})

@app.route('/new-session', methods=['POST'])
def new_session():
    """Créer une nouvelle session de chat"""
    session = get_or_create_session()
    return jsonify({
        'session_id': session.session_id,
        'message': 'Nouvelle session créée'
    })

@app.route('/session-history/<session_id>', methods=['GET'])
def get_session_history(session_id):
    """Récupérer l'historique d'une session"""
    if session_id in chat_sessions:
        session = chat_sessions[session_id]
        return jsonify({
            'session_id': session_id,
            'messages': session.messages,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat()
        })
    else:
        return jsonify({'error': 'Session non trouvée'}), 404

@app.route('/sessions', methods=['GET'])
def list_sessions():
    """Lister toutes les sessions actives"""
    sessions_info = []
    for session_id, session in chat_sessions.items():
        sessions_info.append({
            'session_id': session_id,
            'created_at': session.created_at.isoformat(),
            'last_activity': session.last_activity.isoformat(),
            'message_count': len(session.messages)
        })
    return jsonify({'sessions': sessions_info})

if __name__ == "__main__":
    logger.info("Lancement du serveur Flask...")
    app.run(debug=True, host="0.0.0.0", port=5000)