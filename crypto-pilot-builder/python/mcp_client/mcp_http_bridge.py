#!/usr/bin/env python3
"""
Point d'entrée du Bridge HTTP-MCP
Orchestre tous les modules pour créer l'API complète
"""

import asyncio
from flask import Flask
from flask_cors import CORS

# Imports des modules locaux
from config import HOST, PORT, DEBUG
from mcp_client import mcp_client
from session_manager import session_manager
from api_routes import create_api_routes

def create_app():
    """Factory pour créer l'application Flask"""
    app = Flask(__name__)
    CORS(app)

    # Enregistrement des routes
    create_api_routes(app)

    return app

async def init_mcp():
    """Initialise le client MCP au démarrage"""
    success = await mcp_client.connect()
    if success:
        print("✅ Client MCP initialisé avec succès")
    else:
        print("❌ Échec de l'initialisation MCP")
    return success

def main():
    """Point d'entrée principal"""
    print("🌉 Bridge HTTP-MCP - Version modulaire")
    print("📁 Structure:")
    print("  ├── config.py           # Configuration")
    print("  ├── mcp_client.py       # Client MCP pur")
    print("  ├── session_manager.py  # Gestion sessions")
    print("  ├── api_routes.py       # Routes API")
    print("  └── mcp_http_bridge.py  # Point d'entrée")
    print()

    # Initialisation MCP
    print("🔧 Initialisation du client MCP...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    mcp_ready = loop.run_until_complete(init_mcp())
    loop.close()

    if not mcp_ready:
        print("❌ Impossible de démarrer sans MCP")
        return

    # Création de l'application
    app = create_app()

    print(f"🚀 API disponible sur http://{HOST}:{PORT}")
    print("💡 Endpoints principaux:")
    print("  - POST /chat           # Chat frontend")
    print("  - POST /new-session    # Nouvelle session")
    print("  - GET  /health         # État du service")
    print("  - GET  /mcp/tools      # Outils MCP")
    print()

    # Démarrage du serveur
    app.run(debug=DEBUG, host=HOST, port=PORT)

if __name__ == "__main__":
    main()