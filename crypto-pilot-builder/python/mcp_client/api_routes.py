#!/usr/bin/env python3
"""
Routes API pour l'interface avec le frontend Vue.js
"""

import asyncio
from flask import request, jsonify
from mcp_client import mcp_client
from session_manager import session_manager

def create_api_routes(app):
    """Enregistre toutes les routes API sur l'app Flask"""

    # ===== ROUTES MCP PURES =====

    @app.route('/mcp/connect', methods=['POST'])
    def connect_mcp():
        """Connecte le client au serveur MCP"""
        async def do_connect():
            return await mcp_client.connect()

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(do_connect())
            loop.close()

            if success:
                return jsonify({"status": "connected"})
            else:
                return jsonify({"error": "Connexion échouée"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/mcp/tools', methods=['GET'])
    def list_mcp_tools():
        """Liste les outils MCP disponibles"""
        async def do_list():
            return await mcp_client.list_tools()

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(do_list())
            loop.close()

            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/mcp/call', methods=['POST'])
    def call_mcp_tool():
        """Appelle un outil MCP directement"""
        data = request.get_json()
        if not data or 'tool_name' not in data:
            return jsonify({"error": "tool_name requis"}), 400

        tool_name = data['tool_name']
        arguments = data.get('arguments', {})

        async def do_call():
            return await mcp_client.call_tool(tool_name, arguments)

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(do_call())
            loop.close()

            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ===== ROUTES FRONTEND COMPATIBLES =====

    @app.route('/new-session', methods=['POST'])
    def create_new_session():
        """Compatible avec le frontend - Crée une nouvelle session"""
        session_id = session_manager.create_session()
        return jsonify({'session_id': session_id})

    @app.route('/chat', methods=['POST'])
    def chat():
        """Compatible avec le frontend - Chat intelligent via MCP"""
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Message manquant'}), 400

        user_input = data['message']
        session_id = data.get('session_id')

        # Créer session si nécessaire
        if not session_id:
            session_id = session_manager.create_session()

        try:
            # Sauvegarder le message utilisateur
            session_manager.add_message(session_id, "user", user_input)

            # Construire le contexte de conversation
            context = session_manager.get_context(session_id)

            # Appel MCP pour la conversation
            async def do_chat():
                return await mcp_client.chat(user_input, context)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            chat_result = loop.run_until_complete(do_chat())
            loop.close()

            if not chat_result.get("success", False):
                if "error" in chat_result:
                    raise Exception(chat_result["error"])
                else:
                    raise Exception("Échec de l'appel MCP")

            ai_response = chat_result["result"]

            # Sauvegarder la réponse
            session_manager.add_message(session_id, "assistant", ai_response)

            return jsonify({
                'response': ai_response,
                'session_id': session_id
            })

        except Exception as e:
            error_msg = f"Erreur MCP: {str(e)}"
            session_manager.add_message(session_id, "assistant", error_msg)

            return jsonify({
                'response': error_msg,
                'session_id': session_id
            }), 500

    # ===== ROUTES DE GESTION DES SESSIONS =====

    @app.route('/sessions', methods=['GET'])
    def list_sessions():
        """Liste toutes les sessions actives"""
        sessions = session_manager.list_sessions()
        return jsonify({'sessions': sessions})

    @app.route('/sessions/<session_id>', methods=['GET'])
    def get_session(session_id):
        """Récupère les détails d'une session"""
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session non trouvée'}), 404

        return jsonify({
            'session_id': session_id,
            'messages': session_manager.get_messages(session_id)
        })

    @app.route('/sessions/<session_id>', methods=['DELETE'])
    def delete_session(session_id):
        """Supprime une session"""
        success = session_manager.delete_session(session_id)
        if success:
            return jsonify({'status': 'deleted'})
        else:
            return jsonify({'error': 'Session non trouvée'}), 404

    # ===== ROUTE DE SANTÉ =====

    @app.route('/health', methods=['GET'])
    def health_check():
        """Vérifie l'état du service"""
        return jsonify({
            'status': 'ok',
            'mcp_connected': mcp_client.is_connected(),
            'active_sessions': len(session_manager.sessions)
        })