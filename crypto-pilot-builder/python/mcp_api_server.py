#!/usr/bin/env python3
"""
API Serveur MCP - Remplace chatbot.py (Agno)
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv
import uuid

load_dotenv()

app = Flask(__name__)
CORS(app)

# Sessions en mémoire
sessions = {}

class MCPChatAPI:
    def __init__(self):
        self.openai_client = openai.OpenAI()

    def chat(self, user_message, conversation_history=[]):
        """Conversation avec OpenAI"""
        messages = [
            {
                "role": "system",
                "content": "Tu es un expert crypto qui répond de manière claire, structurée et pédagogique aux questions sur les cryptomonnaies, leurs fonctionnements et leurs placements."
                            "Tu peux expliquer le fonctionnement des actions, indices, ETF, crypto, ou tout autre instrument en lien avec les cryptomonnaies."

                            "Sois rigoureux, neutre et didactique. Utilise des exemples concrets si cela peut aider à comprendre."
                            "Si tu ne peux pas accéder à des données temps réel, précise-le."
                            "Si la question est trop vague, pose une question de clarification."
                            "Soit transparent avec les utilisateurs et ne te trompe pas, précise si tu ne sais pas répondre."
            }
        ] + conversation_history[-10:] + [{"role": "user", "content": user_message}]

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )

        return response.choices[0].message.content

# Instance globale
mcp_chat = MCPChatAPI()

@app.route('/new-session', methods=['POST'])
def create_new_session():
    """Crée une nouvelle session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {'messages': []}
    return jsonify({'session_id': session_id})

@app.route('/chat', methods=['POST'])
def chat():
    """Endpoint principal de chat"""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message manquant'}), 400

    user_input = data['message']
    session_id = data.get('session_id')

    # Créer session si nécessaire
    if not session_id or session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = {'messages': []}

    try:
        # Récupérer l'historique
        conversation_history = sessions[session_id]['messages']

        # Appel OpenAI
        ai_response = mcp_chat.chat(user_input, conversation_history)

        # Sauvegarder dans la session
        sessions[session_id]['messages'].extend([
            {"role": "user", "content": user_input},
            {"role": "assistant", "content": ai_response}
        ])

        return jsonify({
            'response': ai_response,
            'session_id': session_id
        })

    except Exception as e:
        return jsonify({
            'response': f"Erreur: {str(e)}",
            'session_id': session_id
        }), 500

@app.route('/sessions', methods=['GET'])
def list_sessions():
    """Liste les sessions actives"""
    session_list = []
    for session_id, data in sessions.items():
        session_list.append({
            'session_id': session_id,
            'message_count': len(data['messages']),
        })
    return jsonify({'sessions': session_list})

if __name__ == "__main__":
    print("🚀 API Serveur MCP démarré sur http://localhost:5000")
    app.run(debug=True, host="0.0.0.0", port=5000)