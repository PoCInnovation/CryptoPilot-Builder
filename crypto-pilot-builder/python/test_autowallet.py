#!/usr/bin/env python3
"""
Script de test pour le système d'autowallet
"""

import sys
import os
import asyncio
from datetime import datetime

# Ajouter le répertoire parent au path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services import (
    news_service,
    ai_analyzer,
    alert_service,
    autowallet_service
)

def test_news_service():
    """Test du service de news"""
    print("🧪 Test du service de news...")
    
    try:
        # Récupérer les news
        news = news_service.fetch_crypto_news(limit=5)
        print(f"✅ {len(news)} news récupérées")
        
        if news:
            # Analyser le sentiment d'une news
            news_item = news[0]
            sentiment = news_service.analyze_sentiment(news_item)
            relevance = news_service.calculate_relevance(news_item)
            
            print(f"📰 News: {news_item.title[:50]}...")
            print(f"   Sentiment: {sentiment:.2f}")
            print(f"   Pertinence: {relevance:.2f}")
            print(f"   Cryptos mentionnées: {news_item.crypto_mentions}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans le service de news: {e}")
        return False

def test_ai_analyzer():
    """Test de l'analyseur IA"""
    print("\n🧪 Test de l'analyseur IA...")
    
    try:
        # Obtenir le contexte de marché
        market_context = ai_analyzer.get_market_context()
        print(f"✅ Contexte de marché récupéré: {market_context.market_sentiment}")
        
        # Récupérer des news pour l'analyse
        news_items = news_service.get_recent_news(hours=24)
        if news_items:
            # Analyser les news
            alerts = ai_analyzer.analyze_news_for_investment(news_items[:3], market_context)
            print(f"✅ {len(alerts)} alertes générées")
            
            if alerts:
                alert = alerts[0]
                print(f"🚨 Alerte: {alert.alert_type} {alert.crypto_symbol}")
                print(f"   Confiance: {alert.confidence_score:.2f}")
                print(f"   Raisonnement: {alert.reasoning[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans l'analyseur IA: {e}")
        return False

def test_alert_service():
    """Test du service d'alertes"""
    print("\n🧪 Test du service d'alertes...")
    
    try:
        # Vérifier les templates
        templates = alert_service.alert_templates
        print(f"✅ {len(templates)} templates d'alerte disponibles")
        
        # Vérifier la configuration SMTP
        smtp_config = alert_service.smtp_config
        print(f"✅ Configuration SMTP: {smtp_config['smtp_server']}:{smtp_config['smtp_port']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans le service d'alertes: {e}")
        return False

def test_autowallet_service():
    """Test du service principal d'autowallet"""
    print("\n🧪 Test du service principal d'autowallet...")
    
    try:
        # Créer une configuration de test
        test_user_id = "test_user_123"
        test_config = {
            'is_active': True,
            'analysis_interval': 15,
            'max_investment_per_trade': 100.0,
            'risk_tolerance': 'medium',
            'investment_strategy': 'balanced',
            'min_confidence_threshold': 0.7
        }
        
        # Créer l'autowallet
        autowallet_id = autowallet_service.create_autowallet(test_user_id, test_config)
        print(f"✅ Autowallet créé: {autowallet_id}")
        
        # Vérifier le statut
        status = autowallet_service.get_autowallet_status(test_user_id)
        print(f"✅ Statut: {status['is_active']}, Monitoring: {status['is_monitoring']}")
        
        # Nettoyer
        autowallet_service.delete_autowallet(test_user_id)
        print("✅ Autowallet supprimé")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans le service principal: {e}")
        return False

def test_integration():
    """Test d'intégration complète"""
    print("\n🧪 Test d'intégration complète...")
    
    try:
        # Simuler un workflow complet
        test_user_id = "integration_test_456"
        
        # 1. Créer l'autowallet
        config = {
            'is_active': True,
            'analysis_interval': 5,
            'max_investment_per_trade': 50.0,
            'risk_tolerance': 'low',
            'investment_strategy': 'conservative',
            'min_confidence_threshold': 0.8
        }
        
        autowallet_id = autowallet_service.create_autowallet(test_user_id, config)
        print("✅ Étape 1: Autowallet créé")
        
        # 2. Ajouter un canal d'alerte
        channel_id = alert_service.add_alert_channel(
            test_user_id, 
            'email', 
            {'email': 'test@example.com'}
        )
        print("✅ Étape 2: Canal d'alerte ajouté")
        
        # 3. Démarrer le monitoring
        autowallet_service.start_monitoring(test_user_id)
        print("✅ Étape 3: Monitoring démarré")
        
        # 4. Vérifier le statut
        status = autowallet_service.get_autowallet_status(test_user_id)
        print(f"✅ Étape 4: Statut vérifié - Monitoring: {status['is_monitoring']}")
        
        # 5. Nettoyer
        autowallet_service.stop_monitoring(test_user_id)
        autowallet_service.delete_autowallet(test_user_id)
        print("✅ Étape 5: Nettoyage effectué")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans le test d'intégration: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests du système d'autowallet...")
    print("=" * 60)
    
    tests = [
        ("Service de news", test_news_service),
        ("Analyseur IA", test_ai_analyzer),
        ("Service d'alertes", test_alert_service),
        ("Service principal", test_autowallet_service),
        ("Intégration complète", test_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Erreur critique dans {test_name}: {e}")
            results.append((test_name, False))
    
    # Résumé des tests
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés avec succès !")
        return 0
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
