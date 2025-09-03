#!/usr/bin/env python3
"""
Script pour déboguer la création de configuration AutoWallet
"""

import requests
import json
import os

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
        print("   Assurez-vous que le serveur est démarré")
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

def test_config_endpoint():
    """Test de l'endpoint de configuration"""
    print("\n🔧 Test de l'endpoint de configuration")
    print("=" * 50)
    
    url = "http://localhost:5000/api/autowallet/config"
    
    # Test GET (devrait retourner 404 si pas de config)
    print(f"📡 Test GET: {url}")
    try:
        response = requests.get(url, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Réponse: {response.text}")
        
        if response.status_code == 404:
            print("   ✅ Erreur 404 attendue (pas de configuration)")
        else:
            print("   ⚠️  Réponse inattendue")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
    
    # Test POST (création de configuration)
    print(f"\n📡 Test POST: {url}")
    config_data = {
        "is_active": True,
        "analysis_interval": 15,
        "max_investment_per_trade": 100,
        "risk_tolerance": "medium",
        "investment_strategy": "balanced",
        "min_confidence_score": 0.3,
        "max_daily_trades": 10,
        "stop_loss_percentage": 5.0,
        "take_profit_percentage": 15.0
    }
    
    try:
        response = requests.post(url, json=config_data, timeout=10)
        print(f"   Status: {response.status_code}")
        print(f"   Réponse: {response.text}")
        
        if response.status_code == 201:
            print("   ✅ Configuration créée avec succès")
        elif response.status_code == 401:
            print("   ❌ Erreur d'authentification (JWT requis)")
        elif response.status_code == 500:
            print("   ❌ Erreur serveur")
        else:
            print("   ⚠️  Réponse inattendue")
            
    except Exception as e:
        print(f"   ❌ Erreur: {e}")

def check_environment():
    """Vérifie l'environnement"""
    print("\n🌍 Vérification de l'environnement")
    print("=" * 50)
    
    # Vérifier les variables d'environnement
    env_vars = [
        "JWT_SECRET_KEY",
        "NEWS_API_KEY",
        "SMTP_SERVER",
        "SMTP_USERNAME"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:20]}..." if len(value) > 20 else f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Non définie")
    
    # Vérifier la structure des dossiers
    print(f"\n📁 Dossier courant: {os.getcwd()}")
    
    # Vérifier les fichiers importants
    files_to_check = [
        "app.py",
        "mcp_client/autowallet_routes.py",
        "services/autowallet_service.py"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path}")

def check_autowallet_service():
    """Vérifie le service AutoWallet"""
    print("\n🤖 Vérification du service AutoWallet")
    print("=" * 50)
    
    try:
        # Importer le service
        import sys
        sys.path.append('.')
        
        from services.autowallet_service import AutowalletService
        
        # Créer une instance
        service = AutowalletService()
        print("✅ Service AutoWallet importé avec succès")
        
        # Vérifier les méthodes
        methods = [method for method in dir(service) if not method.startswith('_')]
        print(f"✅ Méthodes disponibles: {len(methods)}")
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == "__main__":
    print("🚀 Debug de la création de configuration AutoWallet")
    print("=" * 70)
    
    check_server_status()
    check_environment()
    test_config_endpoint()
    check_autowallet_service()
    
    print("\n📋 Résumé:")
    print("   Si vous obtenez une erreur 401, c'est normal (pas d'authentification)")
    print("   Si vous obtenez une erreur 500, vérifiez les logs du serveur")
    print("   Le problème peut venir de l'import des services")
