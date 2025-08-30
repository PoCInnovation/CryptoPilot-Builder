#!/usr/bin/env python3
"""
Script pour créer une configuration AutoWallet de test
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

def create_autowallet_config():
    """Crée une configuration AutoWallet de test"""
    print("🔧 Création d'une configuration AutoWallet de test")
    print("=" * 60)
    
    # Créer un token JWT de test
    token = create_test_jwt()
    if not token:
        print("❌ Impossible de créer un token de test")
        return False
    
    print(f"✅ Token JWT créé: {token[:50]}...")
    
    # URL de l'endpoint
    url = "http://localhost:5000/api/autowallet/config"
    
    # Configuration de test
    config_data = {
        "is_active": True,
        "analysis_interval": 15,  # 15 minutes
        "max_investment_per_trade": 100,  # $100
        "risk_tolerance": "medium",
        "investment_strategy": "balanced",
        "min_confidence_score": 0.3,
        "max_daily_trades": 10,
        "stop_loss_percentage": 5.0,
        "take_profit_percentage": 15.0
    }
    
    # Headers avec authentification
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\n📡 Création de la configuration: {url}")
    print(f"📊 Configuration: {json.dumps(config_data, indent=2)}")
    
    try:
        response = requests.post(url, json=config_data, headers=headers, timeout=10)
        print(f"\n📊 Réponse reçue:")
        print(f"   Status: {response.status_code}")
        print(f"   Contenu: {response.text}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"\n✅ Configuration créée avec succès !")
            print(f"   ID: {data.get('autowallet_id')}")
            print(f"   Message: {data.get('message')}")
            return True
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
        print(f"❌ Erreur lors de la création: {e}")
    
    return False

def test_config_retrieval():
    """Test de récupération de la configuration"""
    print("\n📋 Test de récupération de la configuration")
    print("=" * 60)
    
    token = create_test_jwt()
    if not token:
        return False
    
    url = "http://localhost:5000/api/autowallet/config"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"📡 Test de récupération: {url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Configuration récupérée")
            print(f"   Active: {data.get('is_active')}")
            print(f"   Intervalle: {data.get('analysis_interval')} minutes")
            print(f"   Investissement max: ${data.get('max_investment_per_trade')}")
            return True
        else:
            print(f"   ❌ Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_analyze_endpoint():
    """Test de l'endpoint d'analyse après création de la config"""
    print("\n🧪 Test de l'endpoint d'analyse")
    print("=" * 60)
    
    token = create_test_jwt()
    if not token:
        return False
    
    url = "http://localhost:5000/api/autowallet/analyze"
    test_data = {
        "news_ids": ["50915331", "50914430"]
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, json=test_data, headers=headers, timeout=10)
        print(f"📡 Test de l'endpoint: {url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {data.get('count', 0)} alertes générées")
            return True
        else:
            print(f"   ❌ Erreur: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Création et test de configuration AutoWallet")
    print("=" * 70)
    
    # Étape 1: Créer la configuration
    if create_autowallet_config():
        print("\n" + "="*70)
        
        # Étape 2: Tester la récupération
        if test_config_retrieval():
            print("\n" + "="*70)
            
            # Étape 3: Tester l'endpoint d'analyse
            test_analyze_endpoint()
    
    print("\n📋 Résumé:")
    print("   Si la configuration est créée avec succès,")
    print("   l'interface AutoWallet devrait fonctionner")
    print("   et le bouton Analyser devrait marcher !")
