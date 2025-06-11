#!/usr/bin/env python3
"""
API routes for interface with Vue.js frontend
"""

import asyncio
from flask import request, jsonify
from mcp_client import mcp_client
from session_manager import session_manager

def create_api_routes(app):
    """Register all API routes on Flask app"""

    # ===== MCP ROUTES =====

    @app.route('/mcp/connect', methods=['POST'])
    def connect_mcp():
        """Connect client to OpenAI agent via MCP"""
        async def do_connect():
            return await mcp_client.connect()

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(do_connect())
            loop.close()

            if success:
                return jsonify({"status": "connected", "agent": "OpenAI CryptoPilot"})
            else:
                return jsonify({"error": "Connection failed"}), 500
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/mcp/tools', methods=['GET'])
    def list_mcp_tools():
        """List available MCP tools"""
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
        """Call MCP tool directly"""
        data = request.get_json()
        if not data or 'tool_name' not in data:
            return jsonify({"error": "tool_name required"}), 400

        crypto_id = data['crypto_id']
        currency = data.get('currency', 'usd')

        async def do_price_call():
            return await mcp_client.get_crypto_price(crypto_id, currency)

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(do_price_call())
            loop.close()

            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/mcp/agent', methods=['POST'])
    def communicate_with_agent():
        """Direct communication with OpenAI agent"""
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "message required"}), 400

        message = data['message']
        context = data.get('context', '')

        async def do_agent_call():
            return await mcp_client.chat(message, context)

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(do_agent_call())
            loop.close()

            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/crypto/price', methods=['POST'])
    def get_crypto_price():
        """Get cryptocurrency price via MCP tool"""
        data = request.get_json()
        if not data or 'crypto_id' not in data:
            return jsonify({"error": "crypto_id required"}), 400

        crypto_id = data['crypto_id']
        currency = data.get('currency', 'eur')

        async def do_price_call():
            return await mcp_client.get_crypto_price(crypto_id, currency)

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(do_price_call())
            loop.close()

            return jsonify(result)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ===== FRONTEND COMPATIBLE ROUTES =====

    @app.route('/new-session', methods=['POST'])
    def create_new_session():
        """Create new session"""
        session_id = session_manager.create_session()
        return jsonify({'session_id': session_id})

    @app.route('/chat', methods=['POST'])
    def chat():
        """Intelligent chat via OpenAI MCP agent"""
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message'}), 400

        user_input = data['message']
        session_id = data.get('session_id')

        # Create session if necessary
        if not session_id:
            session_id = session_manager.create_session()

        try:
            # Save user message
            session_manager.add_message(session_id, "user", user_input)

            # Build conversation context
            context = session_manager.get_context(session_id)

            # Call OpenAI agent via MCP
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
                    raise Exception("Failed to communicate with agent")

            ai_response = chat_result["result"]

            # Save response
            session_manager.add_message(session_id, "assistant", ai_response)

            return jsonify({
                'response': ai_response,
                'session_id': session_id,
                'agent': 'OpenAI CryptoPilot'
            })

        except Exception as e:
            error_msg = f"OpenAI agent error: {str(e)}"
            session_manager.add_message(session_id, "assistant", error_msg)

            return jsonify({
                'response': error_msg,
                'session_id': session_id
            }), 500

    # ===== SESSION MANAGEMENT ROUTES =====

    @app.route('/sessions', methods=['GET'])
    def list_sessions():
        """List all active sessions"""
        sessions = session_manager.list_sessions()
        return jsonify({'sessions': sessions})

    @app.route('/sessions/<session_id>', methods=['GET'])
    def get_session(session_id):
        """Get session details"""
        session = session_manager.get_session(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404

        return jsonify({
            'session_id': session_id,
            'messages': session_manager.get_messages(session_id)
        })

    @app.route('/sessions/<session_id>', methods=['DELETE'])
    def delete_session(session_id):
        """Delete a session"""
        success = session_manager.delete_session(session_id)
        if success:
            return jsonify({'status': 'deleted'})
        else:
            return jsonify({'error': 'Session not found'}), 404

    # ===== HEALTH ROUTE =====

    @app.route('/health', methods=['GET'])
    def health_check():
        """Check service status"""
        return jsonify({
            'status': 'ok',
            'agent': 'OpenAI CryptoPilot',
            'mcp_connected': mcp_client.is_connected(),
            'active_sessions': len(session_manager.sessions),
            'architecture': 'Agent-based with crypto tools',
            'available_tools': ['get_crypto_price']
        })