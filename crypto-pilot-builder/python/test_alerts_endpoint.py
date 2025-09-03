#!/usr/bin/env python3
"""
Script de test pour l'endpoint des alertes
"""

import requests
import json

def test_alerts_endpoint():
    """Test de l'endpoint /api/autowallet/alerts"""
    print("🧪 Test de l'endpoint des alertes")
    print("=" * 50)
    
    # URL de l'endpoint
    url = "http://localhost:5000/api/autowallet/alerts"
    
    print(f"📡 Test de l'endpoint: {url}")
    
    try:
        # Test sans authentification (devrait échouer)
        print("\n🔒 Test sans authentification...")
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Réponse: {response.text}")
        
        if response.status_code == 401:
            print("   ✅ Erreur 401 attendue (pas d'authentification)")
        else:
            print("   ⚠️  Réponse inattendue")
        
        # Test avec un token JWT factice
        print("\n🔑 Test avec token JWT factice...")
        headers = {
            "Authorization": "Bearer fake_token_123",
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Réponse: {response.text}")
        
        if response.status_code == 422:
            print("   ✅ Erreur 422 attendue (token invalide)")
        else:
            print("   ⚠️  Réponse inattendue")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("   Assurez-vous que le serveur est démarré: python app.py")
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

def test_news_endpoint():
    """Test de l'endpoint des news pour vérifier le format"""
    print("\n📰 Test de l'endpoint des news")
    print("=" * 50)
    
    url = "http://localhost:5000/api/autowallet/news"
    
    try:
        print(f"📡 Test de l'endpoint: {url}")
        
        # Test sans authentification
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data.get('news', []))} news récupérées")
            if data.get('news'):
                first_news = data['news'][0]
                print(f"   📊 Format de la première news:")
                print(f"      ID: {first_news.get('id')}")
                print(f"      Title: {first_news.get('title')}")
                print(f"      Crypto mentions: {first_news.get('crypto_mentions')}")
        elif response.status_code == 401:
            print("   ✅ Erreur 401 attendue (pas d'authentification)")
        else:
            print(f"   ⚠️  Réponse inattendue: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    print("🚀 Test des endpoints AutoWallet")
    print("=" * 60)
    
    # Test de l'endpoint des alertes
    test_alerts_endpoint()
    
    # Test de l'endpoint des news
    test_news_endpoint()
    
    print("\n📋 Résumé:")
    print("   Si vous obtenez des erreurs 401/422, c'est normal")
    print("   Le problème peut venir du format des données")
    print("   Vérifiez les logs du serveur et de la console navigateur")
