#!/usr/bin/env python3
"""
Chatbot interactif avec outils MCP - Version simple
Remplace Agno pour converser avec l'IA
"""

import openai
from dotenv import load_dotenv
from simple_mcp_server import SimpleMCPServer
import re

# Charger les variables d'environnement
load_dotenv()

class ChatBotMCP:
    """Chatbot qui utilise des outils MCP"""
    
    def __init__(self):
        self.server = SimpleMCPServer()
        self.client = openai.OpenAI()
        self.conversation = []
        
        # Description des outils pour l'IA
        self.tools_description = self._build_tools_description()
        
    def _build_tools_description(self):
        """Construit la description des outils pour l'IA"""
        desc = "Tu peux utiliser ces outils :\n"
        for name, info in self.server.tools.items():
            desc += f"- {name}: {info['description']}\n"
        desc += "\nSi l'utilisateur demande quelque chose qui correspond à un outil, utilise-le !"
        return desc
    
    def _detect_tool_usage(self, user_message):
        """Détecte si l'utilisateur veut utiliser un outil"""
        message_lower = user_message.lower()
        
        # Détection pour "hello"
        hello_patterns = [r'bonjour\s+(\w+)', r'salut\s+(\w+)', r'hello\s+(\w+)', r'dis bonjour à\s+(\w+)']
        for pattern in hello_patterns:
            match = re.search(pattern, message_lower)
            if match:
                name = match.group(1).capitalize()
                return "hello", {"name": name}
        
        # Détection pour "add"
        add_patterns = [
            r'calcule?\s+(\d+)\s*\+\s*(\d+)',
            r'additionne?\s+(\d+)\s+et\s+(\d+)',
            r'(\d+)\s*\+\s*(\d+)\s*=?\s*\?',
            r'combien fait\s+(\d+)\s*\+\s*(\d+)'
        ]
        for pattern in add_patterns:
            match = re.search(pattern, message_lower)
            if match:
                a = int(match.group(1))
                b = int(match.group(2))
                return "add", {"a": a, "b": b}
        
        return None, None
    
    def _call_openai(self, user_message):
        """Appelle OpenAI avec le contexte des outils"""
        # Ajouter le message utilisateur
        self.conversation.append({"role": "user", "content": user_message})
        
        # Construire les messages pour OpenAI
        messages = [
            {
                "role": "system",
                "content": f"""Tu es un assistant intelligent et amical. 

{self.tools_description}

IMPORTANT : Si tu détectes qu'un outil peut être utilisé, réponds d'abord normalement, puis ajoute à la fin de ta réponse :
[OUTIL: nom_outil {{"parametre": "valeur"}}]

Par exemple :
- Si on dit "bonjour Alice" → réponds normalement + [OUTIL: hello {{"name": "Alice"}}]
- Si on dit "calcule 5+3" → réponds normalement + [OUTIL: add {{"a": 5, "b": 3}}]

Sois naturel et conversationnel !"""
            }
        ]
        
        # Ajouter l'historique récent
        messages.extend(self.conversation[-10:])  # Garder les 10 derniers messages
        
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content
        self.conversation.append({"role": "assistant", "content": ai_response})
        
        return ai_response
    
    def _process_tool_calls(self, ai_response):
        """Traite les appels d'outils dans la réponse de l'IA"""
        # Chercher des patterns [OUTIL: ...]
        tool_pattern = r'\[OUTIL:\s*(\w+)\s+({[^}]+})\]'
        matches = re.findall(tool_pattern, ai_response)
        
        results = []
        clean_response = ai_response
        
        for tool_name, args_str in matches:
            try:
                # Parser les arguments JSON
                import json
                args = json.loads(args_str)
                
                # Appeler l'outil
                result = self.server.call_tool(tool_name, args)
                results.append(f"🔧 {result}")
                
                # Nettoyer la réponse
                clean_response = re.sub(r'\[OUTIL:[^]]+\]', '', clean_response).strip()
                
            except Exception as e:
                results.append(f"❌ Erreur outil {tool_name}: {e}")
        
        return clean_response, results
    
    def chat_turn(self, user_message):
        """Un tour de conversation"""
        print(f"\n💬 Vous: {user_message}")
        
        try:
            # 1. Essayer détection automatique d'outils
            tool_name, tool_args = self._detect_tool_usage(user_message)
            
            if tool_name:
                # Outil détecté automatiquement
                tool_result = self.server.call_tool(tool_name, tool_args)
                
                # Aussi demander à OpenAI une réponse naturelle
                ai_response = self._call_openai(user_message)
                clean_response = re.sub(r'\[OUTIL:[^]]+\]', '', ai_response).strip()
                
                print(f"🤖 Assistant: {clean_response}")
                print(f"🔧 Outil {tool_name}: {tool_result}")
                
            else:
                # 2. Laisser OpenAI décider
                ai_response = self._call_openai(user_message)
                clean_response, tool_results = self._process_tool_calls(ai_response)
                
                print(f"🤖 Assistant: {clean_response}")
                for result in tool_results:
                    print(result)
                    
        except Exception as e:
            print(f"❌ Erreur: {e}")
            print("💡 Vérifiez votre clé OpenAI dans .env")

    def start_chat(self):
        """Démarre la conversation interactive"""
        print("🚀 ChatBot MCP - Version Simple")
        print("=" * 50)
        print(f"🛠️ Outils disponibles: {list(self.server.tools.keys())}")
        print("💡 Exemples:")
        print("   - 'Bonjour Alice'")
        print("   - 'Calcule 15 + 27'") 
        print("   - 'Comment ça va ?'")
        print("   - 'quit' pour quitter")
        print("=" * 50)
        
        while True:
            try:
                user_input = input("\n💬 Vous: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'au revoir']:
                    print("\n👋 Au revoir !")
                    break
                
                if not user_input:
                    continue
                    
                self.chat_turn(user_input)
                
            except KeyboardInterrupt:
                print("\n\n👋 Au revoir !")
                break
            except EOFError:
                break

def main():
    """Point d'entrée"""
    chatbot = ChatBotMCP()
    chatbot.start_chat()

if __name__ == "__main__":
    main() 