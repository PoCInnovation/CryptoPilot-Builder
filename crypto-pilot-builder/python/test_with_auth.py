#!/usr/bin/env python3
"""
Script de test pour l'endpoint d'analyse avec authentification simulée
"""

import requests
import json
from datetime import datetime, timedelta
import jwt

def create_test_jwt():
    """Crée un token JWT de test"""
    # Clé secrète de test (doit correspondre à celle du serveur)
    secret_key = "your-secret-key"  # Remplacez par votre vraie clé secrète
    
    # Payload du token
    payload = {
        "user_id": "test_user_123",
        "username": "test_user",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    
    try:
        # Créer le token
        token = jwt.encode(payload, secret_key, algorithm="HS256")
        return token
    except Exception as e:
        print(f"❌ Erreur lors de la création du token: {e}")
        return None

def test_analyze_with_auth():
    """Test de l'endpoint avec authentification"""
    print("🔐 Test de l'endpoint d'analyse avec authentification")
    print("=" * 60)
    
    # Créer un token JWT de test
    token = create_test_jwt()
    if not token:
        print("❌ Impossible de créer un token de test")
        return
    
    print(f"✅ Token JWT créé: {token[:50]}...")
    
    # URL de l'endpoint
    url = "http://localhost:5000/api/autowallet/analyze"
    
    # Données de test
    test_data = {
        "news_ids": ["50915331", "50914430"]
    }
    
    # Headers avec authentification
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📡 Test de l'endpoint: {url}")
    print(f"📊 Données envoyées: {json.dumps(test_data, indent=2)}")
    print(f"🔑 Headers: {json.dumps({k: v[:50] + '...' if k == 'Authorization' else v for k, v in headers.items()}, indent=2)}")
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=10)
        print(f"\n📊 Réponse reçue:")
        print(f"   Status: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Contenu: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ Succès !")
            print(f"   {data.get('count', 0)} alertes générées")
            if 'alerts' in data:
                for i, alert in enumerate(data['alerts'][:3]):
                    print(f"   {i+1}. {alert['alert_type'].upper()} {alert['crypto_symbol']} - {alert['confidence_score']:.2f}")
        elif response.status_code == 401:
            print(f"\n❌ Erreur d'authentification")
            print("   Vérifiez que la clé secrète correspond à celle du serveur")
        elif response.status_code == 500:
            print(f"\n❌ Erreur serveur")
            print("   Vérifiez les logs du serveur")
        else:
            print(f"\n⚠️  Réponse inattendue")
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter au serveur")
        print("   Assurez-vous que le serveur est démarré: python app.py")
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

def test_news_with_auth():
    """Test de l'endpoint des news avec authentification"""
    print("\n📰 Test de l'endpoint des news avec authentification")
    print("=" * 60)
    
    token = create_test_jwt()
    if not token:
        return
    
    url = "http://localhost:5000/api/autowallet/news"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📡 Test de l'endpoint: {url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {len(data.get('news', []))} news récupérées")
        else:
            print(f"   ❌ Erreur: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")

if __name__ == "__main__":
    print("🚀 Test des endpoints AutoWallet avec authentification")
    print("=" * 70)
    
    # Test de l'endpoint d'analyse
    test_analyze_with_auth()
    
    # Test de l'endpoint des news
    test_news_with_auth()
    
    print("\n📋 Résumé:")
    print("   Si vous obtenez une erreur 401, vérifiez la clé secrète")
    print("   Si vous obtenez une erreur 500, vérifiez les logs du serveur")
    print("   Si tout fonctionne, le problème vient du frontend")
