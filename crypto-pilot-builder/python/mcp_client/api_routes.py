#!/usr/bin/env python3
"""
API routes for interface with Vue.js frontend
"""

import asyncio
import os
import re
import json
from datetime import timedelta
from flask import request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from mcp_client import mcp_client
from session_manager import session_manager
import uuid

# Extensions d'authentification
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_api_routes(app):
    """Register all API routes on Flask app"""

    # ===== AUTHENTICATION SETUP =====
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        postgres_host = os.getenv('POSTGRES_HOST', 'localhost')
        app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('POSTGRES_USER', 'cryptopilot_user')}:{os.getenv('POSTGRES_PASSWORD', 'cryptopilot_password')}@{postgres_host}/{os.getenv('POSTGRES_DB', 'cryptopilot')}"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'votre-clé-secrète-super-sécurisée')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        username = db.Column(db.String(50), unique=True, nullable=False)
        email = db.Column(db.String(100), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        wallet_address = db.Column(db.String(42), nullable=True)
        created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
        
        # Relation avec les configurations d'agent
        agent_configs = db.relationship('AgentConfig', backref='user', lazy=True, cascade='all, delete-orphan')

    class AgentConfig(db.Model):
        __tablename__ = 'agent_configs'
        id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
        
        # Configuration IA
        selected_model = db.Column(db.String(100), nullable=False)
        api_key = db.Column(db.Text, nullable=False)  # Chiffré en production
        
        # Configuration des modules
        modules_config = db.Column(db.JSON, nullable=True, default=dict)
        
        # Comportement de l'assistant
        prompt = db.Column(db.Text, nullable=True)
        
        # Métadonnées
        name = db.Column(db.String(100), nullable=False, default='Mon Assistant')
        description = db.Column(db.Text, nullable=True)
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
        updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_password(password):
        if len(password) < 8:
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True

    with app.app_context():
        try:
            db.create_all()
            print("✅ Tables d'authentification et de configuration créées")
        except Exception as e:
            print(f"❌ Erreur lors de la création des tables: {e}")

    # ===== AUTHENTICATION ROUTES =====

    @app.route('/register', methods=['POST'])
    def register():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Aucune donnée fournie'}), 400
            email = data.get('email', '').strip().lower()
            username = data.get('username', '').strip()
            password = data.get('password', '')
            if not email or not username or not password:
                return jsonify({'error': 'Email, nom d\'utilisateur et mot de passe sont requis'}), 400
            if not validate_email(email):
                return jsonify({'error': 'Format d\'email invalide'}), 400
            if len(username) < 3 or len(username) > 80:
                return jsonify({'error': 'Le nom d\'utilisateur doit contenir entre 3 et 80 caractères'}), 400
            if not validate_password(password):
                return jsonify({'error': 'Le mot de passe doit contenir au moins 8 caractères, une majuscule, une minuscule et un chiffre'}), 400
            if User.query.filter_by(email=email).first():
                return jsonify({'error': 'Un utilisateur avec cet email existe déjà'}), 409
            if User.query.filter_by(username=username).first():
                return jsonify({'error': 'Ce nom d\'utilisateur est déjà pris'}), 409
            password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(
                email=email,
                username=username,
                password_hash=password_hash
            )
            db.session.add(new_user)
            db.session.commit()
            access_token = create_access_token(identity=new_user.id)
            return jsonify({
                'message': 'Utilisateur créé avec succès',
                'user': {
                    'id': new_user.id,
                    'email': new_user.email,
                    'username': new_user.username,
                    'created_at': new_user.created_at.isoformat()
                },
                'access_token': access_token
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

    @app.route('/login', methods=['POST'])
    def login():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Aucune donnée fournie'}), 400
            login_field = data.get('email') or data.get('username')
            password = data.get('password')
            if not login_field or not password:
                return jsonify({'error': 'Email/nom d\'utilisateur et mot de passe sont requis'}), 400
            user = None
            if '@' in login_field:
                user = User.query.filter_by(email=login_field.strip().lower()).first()
            else:
                user = User.query.filter_by(username=login_field.strip()).first()
            if not user or not bcrypt.check_password_hash(user.password_hash, password):
                return jsonify({'error': 'Identifiants invalides'}), 401
            access_token = create_access_token(identity=user.id)
            return jsonify({
                'message': 'Connexion réussie',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'username': user.username,
                    'created_at': user.created_at.isoformat()
                },
                'access_token': access_token
            }), 200
        except Exception as e:
            return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

    # ===== AGENT CONFIGURATION ROUTES =====

    @app.route('/agent-config', methods=['POST'])
    @jwt_required()
    def create_agent_config():
        """Créer ou mettre à jour la configuration de l'agent"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Aucune donnée fournie'}), 400
            
            # Validation des données requises
            selected_model = data.get('selectedModel')
            api_key = data.get('apiKey')
            
            if not selected_model or not api_key:
                return jsonify({'error': 'Modèle et clé API sont requis'}), 400
            
            # Chercher une configuration existante pour cet utilisateur
            existing_config = AgentConfig.query.filter_by(user_id=user_id, is_active=True).first()
            
            if existing_config:
                # Mettre à jour la configuration existante
                existing_config.selected_model = selected_model
                existing_config.api_key = api_key
                existing_config.modules_config = data.get('modules', {})
                existing_config.prompt = data.get('prompt', '')
                existing_config.name = data.get('name', 'Mon Assistant')
                existing_config.description = data.get('description', '')
                existing_config.updated_at = db.func.current_timestamp()
                
                config = existing_config
            else:
                # Créer une nouvelle configuration
                config = AgentConfig(
                    user_id=user_id,
                    selected_model=selected_model,
                    api_key=api_key,
                    modules_config=data.get('modules', {}),
                    prompt=data.get('prompt', ''),
                    name=data.get('name', 'Mon Assistant'),
                    description=data.get('description', '')
                )
                db.session.add(config)
            
            db.session.commit()
            
            return jsonify({
                'message': 'Configuration sauvegardée avec succès',
                'config': {
                    'id': config.id,
                    'selectedModel': config.selected_model,
                    'apiKey': config.api_key[-4:] + '...' if config.api_key else '',  # Masquer la clé
                    'modules': config.modules_config,
                    'prompt': config.prompt,
                    'name': config.name,
                    'description': config.description,
                    'createdAt': config.created_at.isoformat(),
                    'updatedAt': config.updated_at.isoformat()
                }
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

    @app.route('/agent-config', methods=['GET'])
    @jwt_required()
    def get_agent_config():
        """Récupérer la configuration active de l'agent"""
        try:
            user_id = get_jwt_identity()
            config = AgentConfig.query.filter_by(user_id=user_id, is_active=True).first()
            
            if not config:
                return jsonify({'error': 'Aucune configuration trouvée'}), 404
            
            return jsonify({
                'config': {
                    'id': config.id,
                    'selectedModel': config.selected_model,
                    'apiKey': config.api_key,  # Retourner la clé complète pour l'utilisation
                    'modules': config.modules_config,
                    'prompt': config.prompt,
                    'name': config.name,
                    'description': config.description,
                    'createdAt': config.created_at.isoformat(),
                    'updatedAt': config.updated_at.isoformat()
                }
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

    @app.route('/agent-config/partial', methods=['PUT'])
    @jwt_required()
    def update_partial_config():
        """Mettre à jour partiellement la configuration (pour les étapes du wizard)"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data:
                return jsonify({'error': 'Aucune donnée fournie'}), 400
            
            # Chercher ou créer une configuration
            config = AgentConfig.query.filter_by(user_id=user_id, is_active=True).first()
            
            if not config:
                config = AgentConfig(
                    user_id=user_id,
                    selected_model='',
                    api_key='',
                    modules_config={},
                    prompt=''
                )
                db.session.add(config)
            
            # Mettre à jour les champs fournis
            if 'selectedModel' in data:
                config.selected_model = data['selectedModel']
            if 'apiKey' in data:
                config.api_key = data['apiKey']
            if 'modules' in data:
                config.modules_config = data['modules']
            if 'prompt' in data:
                config.prompt = data['prompt']
            if 'name' in data:
                config.name = data['name']
            if 'description' in data:
                config.description = data['description']
            
            config.updated_at = db.func.current_timestamp()
            db.session.commit()
            
            return jsonify({
                'message': 'Configuration mise à jour avec succès',
                'config': {
                    'id': config.id,
                    'selectedModel': config.selected_model,
                    'apiKey': config.api_key[-4:] + '...' if config.api_key else '',
                    'modules': config.modules_config,
                    'prompt': config.prompt,
                    'name': config.name,
                    'description': config.description,
                    'updatedAt': config.updated_at.isoformat()
                }
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

    @app.route('/agent-configs', methods=['GET'])
    @jwt_required()
    def list_agent_configs():
        """Lister toutes les configurations de l'utilisateur"""
        try:
            user_id = get_jwt_identity()
            configs = AgentConfig.query.filter_by(user_id=user_id).order_by(AgentConfig.created_at.desc()).all()
            
            configs_data = []
            for config in configs:
                configs_data.append({
                    'id': config.id,
                    'name': config.name,
                    'description': config.description,
                    'selectedModel': config.selected_model,
                    'isActive': config.is_active,
                    'createdAt': config.created_at.isoformat(),
                    'updatedAt': config.updated_at.isoformat()
                })
            
            return jsonify({'configs': configs_data}), 200
            
        except Exception as e:
            return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500

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

    @app.route('/crypto/price', methods=['POST'])
    def get_crypto_price():
        """Get cryptocurrency price via MCP tool"""
        data = request.get_json()
        if not data or 'crypto_id' not in data:
            return jsonify({"error": "crypto_id required"}), 400

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

    # ===== FRONTEND ROUTES =====

    @app.route('/new-session', methods=['POST'])
    def create_new_session():
        """Create new session"""
        session_id = session_manager.create_session()
        return jsonify({'session_id': session_id})

    @app.route('/chat', methods=['POST'])
    @jwt_required()
    def chat():
        """Intelligent chat via OpenAI MCP agent with user config"""
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({'error': 'Missing message'}), 400

        user_input = data['message']
        session_id = data.get('session_id')
        user_id = get_jwt_identity()

        # Récupérer la configuration de l'utilisateur
        config = AgentConfig.query.filter_by(user_id=user_id, is_active=True).first()
        if not config:
            return jsonify({'error': 'Aucune configuration d\'agent trouvée. Veuillez configurer votre agent d\'abord.'}), 400

        # Create session if necessary
        if not session_id:
            session_id = session_manager.create_session()

        try:
            # Save user message
            session_manager.add_message(session_id, "user", user_input)

            # Build conversation context with user config
            conversation_history = session_manager.get_context(session_id)
            context = {
                'conversation_history': conversation_history,
                'agent_config': {
                    'model': config.selected_model,
                    'prompt': config.prompt,
                    'modules': config.modules_config
                }
            }

            # Call OpenAI agent via MCP with user configuration
            async def do_chat():
                return await mcp_client.chat_with_config(user_input, context, config.api_key)

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
                'agent': config.name,
                'model': config.selected_model
            })

        except Exception as e:
            error_msg = f"Agent error: {str(e)}"
            session_manager.add_message(session_id, "assistant", error_msg)

            return jsonify({
                'response': error_msg,
                'session_id': session_id
            }), 500

    # ===== SESSION MANAGEMENT =====

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

    # ===== HEALTH =====

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