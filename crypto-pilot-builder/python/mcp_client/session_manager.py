#!/usr/bin/env python3
"""
Session manager for MCP bridge
"""

import uuid
from typing import Dict, List, Optional
from config import MAX_CONTEXT_MESSAGES

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Dict] = {}

    def create_session(self) -> str:
        """Create new session and return its ID"""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            'messages': [],
            'conversation_context': ""
        }
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        return self.sessions.get(session_id)

    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                'messages': [],
                'conversation_context': ""
            }

        self.sessions[session_id]['messages'].append({
            "role": role,
            "content": content
        })

    def get_context(self, session_id: str) -> str:
        """Build conversation context for recent messages"""
        if session_id not in self.sessions:
            return ""

        messages = self.sessions[session_id]['messages']
        recent_messages = messages[-MAX_CONTEXT_MESSAGES:]

        return "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in recent_messages
        ])

    def get_messages(self, session_id: str) -> List[Dict]:
        """Get all messages from session"""
        if session_id not in self.sessions:
            return []
        return self.sessions[session_id]['messages']

    def delete_session(self, session_id: str) -> bool:
        """Delete session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def list_sessions(self) -> List[Dict]:
        """List all active sessions"""
        session_list = []
        for session_id, data in self.sessions.items():
            session_list.append({
                'session_id': session_id,
                'message_count': len(data['messages']),
                'last_message': data['messages'][-1]['content'] if data['messages'] else None
            })
        return session_list

# Global instance
session_manager = SessionManager()