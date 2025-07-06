#!/usr/bin/env python3
"""
Session manager for MCP bridge - Database version
"""

import uuid
import logging
from typing import Dict, List, Optional
from datetime import datetime

# Configuration du logging
logger = logging.getLogger(__name__)

class SessionManager:
    def __init__(self, db=None):
        """Initialize with database connection"""
        self.db = db
        self.ChatSession = None
        self.ChatMessage = None
        logger.info("SessionManager initialisé")

    def set_models(self, ChatSession, ChatMessage):
        """Set database models"""
        self.ChatSession = ChatSession
        self.ChatMessage = ChatMessage
        logger.info("Modèles de base de données configurés")

    def create_session(self, user_id: str = None, session_name: str = "New Chat") -> str:
        """Create new session and return its ID"""
        if not self.db:
            logger.error("Base de données non initialisée")
            raise Exception("Base de données non initialisée")
        
        if not self.ChatSession:
            logger.error("Modèle ChatSession non configuré")
            raise Exception("Modèle ChatSession non configuré")

        try:
            session_id = str(uuid.uuid4())
            session = self.ChatSession(
                id=session_id,
                user_id=user_id,
                session_name=session_name
            )
            
            self.db.session.add(session)
            self.db.session.commit()
            
            return session_id
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de session: {e}")
            if self.db:
                self.db.session.rollback()
            raise

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        if not self.db or not self.ChatSession:
            logger.error("Base de données ou modèle ChatSession non initialisé")
            return None

        session = self.ChatSession.query.get(session_id)
        if not session:
            return None

        result = {
            'id': str(session.id) if session.id else None,
            'user_id': str(session.user_id) if session.user_id else None,
            'session_name': session.session_name,
            'created_at': session.created_at.isoformat() if session.created_at else None,
            'updated_at': session.updated_at.isoformat() if session.updated_at else None
        }
        
        return result

    def add_message(self, session_id: str, role: str, content: str) -> str:
        """Add message to session and return message ID"""
        if not self.db or not self.ChatMessage or not self.ChatSession:
            return None

        try:
            # Créer la session si elle n'existe pas
            session = self.ChatSession.query.get(session_id)
            if not session:
                session = self.ChatSession(
                    id=session_id,
                    session_name='New Chat'
                )
                self.db.session.add(session)

            # Générer un ID pour le message
            message_id = str(uuid.uuid4())
            
            # Ajouter le message
            message = self.ChatMessage(
                id=message_id,
                session_id=session_id,
                role=role,
                content=content
            )
            self.db.session.add(message)
            
            # Mettre à jour le timestamp de la session
            session.updated_at = datetime.utcnow()
            
            self.db.session.commit()
            
            return message_id
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de message: {e}")
            if self.db:
                self.db.session.rollback()
            return None

    def get_context(self, session_id: str, max_messages: int = 10) -> str:
        """Build conversation context for recent messages"""
        if not self.db or not self.ChatMessage:
            return ""

        messages = self.ChatMessage.query.filter_by(session_id=session_id)\
                                        .order_by(self.ChatMessage.created_at.desc())\
                                        .limit(max_messages).all()
        
        # Inverser l'ordre pour avoir les messages du plus ancien au plus récent
        messages = list(reversed(messages))

        context_lines = []
        for msg in messages:
            if msg.role == 'user':
                context_lines.append(f"Utilisateur: {msg.content}")
            elif msg.role == 'assistant':
                context_lines.append(f"Assistant: {msg.content}")
            elif msg.role == 'system':
                context_lines.append(f"Système: {msg.content}")

        return "\n".join(context_lines)

    def get_messages(self, session_id: str) -> List[Dict]:
        """Get all messages from session"""
        if not self.db or not self.ChatMessage:
            return []

        messages = self.ChatMessage.query.filter_by(session_id=session_id)\
                                        .order_by(self.ChatMessage.created_at).all()

        return [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat()
            }
            for msg in messages
        ]

    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        if not self.db or not self.ChatSession:
            return False

        session = self.ChatSession.query.get(session_id)
        if not session:
            return False

        try:
            self.db.session.delete(session)
            self.db.session.commit()
            return True
        except Exception:
            self.db.session.rollback()
            return False

    def list_sessions(self, user_id: str = None) -> List[Dict]:
        """List all sessions, optionally filtered by user"""
        if not self.db or not self.ChatSession or not self.ChatMessage:
            return []

        query = self.ChatSession.query
        if user_id:
            query = query.filter_by(user_id=user_id)

        sessions = query.order_by(self.ChatSession.updated_at.desc()).all()

        session_list = []
        for session in sessions:
            # Compter les messages
            message_count = self.ChatMessage.query.filter_by(session_id=session.id).count()
            
            # Récupérer le dernier message
            last_message = self.ChatMessage.query.filter_by(session_id=session.id)\
                                                .order_by(self.ChatMessage.created_at.desc()).first()

            session_list.append({
                'session_id': str(session.id) if session.id else None,
                'session_name': session.session_name,
                'user_id': str(session.user_id) if session.user_id else None,
                'message_count': message_count,
                'last_message': last_message.content if last_message else None,
                'last_message_time': last_message.created_at.isoformat() if last_message else None,
                'created_at': session.created_at.isoformat(),
                'updated_at': session.updated_at.isoformat()
            })

        return session_list

    def rename_session(self, session_id: str, new_name: str) -> bool:
        """Rename a session"""
        if not self.db or not self.ChatSession:
            return False

        session = self.ChatSession.query.get(session_id)
        if not session:
            return False

        try:
            session.session_name = new_name.strip()
            session.updated_at = datetime.utcnow()
            self.db.session.commit()
            return True
        except Exception:
            self.db.session.rollback()
            return False

    @property
    def sessions(self) -> Dict:
        """Compatibility property for existing code"""
        if not self.db or not self.ChatSession:
            return {}
        
        # Retourner un dictionnaire des sessions pour compatibilité
        sessions_list = self.list_sessions()
        return {s['session_id']: s for s in sessions_list}

# Instance globale
session_manager = SessionManager()