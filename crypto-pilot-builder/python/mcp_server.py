#!/usr/bin/env python3
"""
Serveur MCP minimal - Base fonctionnelle sans outils compliqués
"""

import asyncio
import sys
import json

async def main():
    """Mini Serveur MCP"""
    print("🚀 Serveur MCP minimal démarré...", file=sys.stderr)

    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break

            # JSON message parsing
            try:
                message = json.loads(line.strip())
                print(f"📨 Message reçu: {message}", file=sys.stderr)


                response = handle_message(message)

                # Send response
                print(json.dumps(response))
                sys.stdout.flush()

            except json.JSONDecodeError:
                print(f"❌ Message JSON invalide: {line}", file=sys.stderr)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"❌ Erreur: {e}", file=sys.stderr)

def handle_message(message):
    """Traite un message MCP"""

    msg_type = message.get("method", "")
    msg_id = message.get("id")

    if msg_type == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "minimal-mcp-server",
                    "version": "1.0.0"
                }
            }
        }

        elif msg_type == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "tools": []
            }
        }

        elif msg_type == "tools/call":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": "Aucun outil disponible"
            }
        }

    else:
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "error": {
                "code": -32601,
                "message": f"Méthode non supportée: {msg_type}"
            }
        }

if __name__ == "__main__":
    asyncio.run(main())