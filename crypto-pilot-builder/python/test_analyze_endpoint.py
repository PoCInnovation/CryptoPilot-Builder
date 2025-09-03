#!/usr/bin/env python3
"""
Script de test pour l'endpoint d'analyse des news
"""

import requests
import json

def test_analyze_endpoint():
    """Test de l'endpoint /api/autowallet/analyze"""
    print("🧪 Test de l'endpoint d'analyse des news")
    print("=" * 50)
    
    # URL de l'endpoint
    url = "http://localhost:5000/api/autowallet/analyze"
    
    # Données de test
    test_data = {
        "news_ids": ["50915331", "50914430"],  # IDs de news réels
        "analysis_type": "individual"
    }
    
    print(f"📡 Test de l'endpoint: {url}")
    print(f"📊 Données envoyées: {json.dumps(test_data, indent=2)}")
    
    try:
        # Test sans authentification (devrait échouer)
        print("\n🔒 Test sans authentification...")
        response = requests.post(url, json=test_data, timeout=10)
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
        response = requests.post(url, json=test_data, headers=headers, timeout=10)
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
    """Test de l'endpoint /api/autowallet/news"""
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
        elif response.status_code == 401:
            print("   ✅ Erreur 401 attendue (pas d'authentification)")
        else:
            print(f"   ⚠️  Réponse inattendue: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

def check_server_status():
    """Vérifie le statut du serveur"""
    print("🔍 Vérification du statut du serveur")
    print("=" * 50)
    
    try:
        # Test de la page d'accueil
        response = requests.get("http://localhost:5000/", timeout=5)
        print(f"✅ Serveur accessible - Status: {response.status_code}")
        
        # Test de l'endpoint de santé
        health_response = requests.get("http://localhost:5000/api/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Endpoint de santé accessible")
        else:
            print(f"⚠️  Endpoint de santé: {health_response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Serveur non accessible sur localhost:5000")
        print("   Vérifiez que le serveur est démarré")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

if __name__ == "__main__":
    print("🚀 Test des endpoints AutoWallet")
    print("=" * 60)
    
    # Vérifier le statut du serveur
    check_server_status()
    
    # Tester les endpoints
    test_news_endpoint()
    test_analyze_endpoint()
    
    print("\n📋 Résumé:")
    print("   Si vous obtenez des erreurs 401/422, c'est normal")
    print("   Le problème peut venir de l'interface frontend")
    print("   Vérifiez les logs du serveur et de la console navigateur")
