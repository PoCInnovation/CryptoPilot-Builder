#!/usr/bin/env python3
"""
Script de test pour vérifier la connexion LibertAI
"""
import asyncio
import os
from dotenv import load_dotenv

async def test_libertai_connection():
    """Test de la connexion LibertAI"""
    
    # Clé API LibertAI (à remplacer par votre vraie clé)
    api_key = "d56d770931ba135ae02b68ed32c8dcf4"
    
    if not api_key:
        print("❌ Aucune clé API LibertAI trouvée")
        return False
    
    print(f"🔑 Clé API trouvée: {api_key[:8]}...")
    
    try:
        import openai
        
        # Créer le client LibertAI
        client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.libertai.io/v1"
        )<
        
        print("✅ Client LibertAI créé avec succès")
        
        # Test simple
        print("🧪 Test de connexion avec LibertAI...")
        
        try:
            response = await client.chat.completions.create(
                model="hermes-3-8b",
                messages=[
                    {"role": "user", "content": "Hello! Can you respond with just 'OK'?"}
                ],
                max_tokens=10,
                temperature=0.1
            )
            
            print(f"📡 Réponse reçue: {response}")
            print(f"📡 Type de réponse: {type(response)}")
            
            if response:
                print(f"📡 Attributs de la réponse: {dir(response)}")
                if hasattr(response, 'choices'):
                    print(f"📡 Choices: {response.choices}")
                    if response.choices:
                        print(f"📡 Premier choice: {response.choices[0]}")
                        if hasattr(response.choices[0], 'message'):
                            print(f"📡 Message: {response.choices[0].message}")
                            content = response.choices[0].message.content
                            print(f"✅ Contenu de la réponse: '{content}'")
                            return True
                        else:
                            print("❌ Pas d'attribut 'message' dans choices[0]")
                    else:
                        print("❌ Liste choices vide")
                else:
                    print("❌ Pas d'attribut 'choices' dans la réponse")
            else:
                print("❌ Réponse None ou False")
                
            return False
            
        except Exception as api_error:
            print(f"❌ Erreur API LibertAI: {api_error}")
            print(f"❌ Type d'erreur: {type(api_error)}")
            return False
            
    except ImportError as e:
        print(f"❌ Module openai non installé: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test de connexion LibertAI...")
    
    success = asyncio.run(test_libertai_connection())
    
    if success:
        print("🎉 Test réussi ! LibertAI fonctionne correctement.")
    else:
        print("💥 Test échoué. Vérifiez votre configuration.")
