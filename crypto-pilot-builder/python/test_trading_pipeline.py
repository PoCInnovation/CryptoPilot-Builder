#!/usr/bin/env python3
"""
Script de test pour la pipeline de trading unifiée
"""

import sys
import os
import time
import logging
from datetime import datetime

# Ajouter le répertoire parent au path Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.trading_pipeline_service import trading_pipeline_service
from config.trading_pipeline_config import PIPELINE_CONFIG

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def test_pipeline_configuration():
    """Test de la configuration de la pipeline"""
    print("🔧 Test de la configuration...")
    
    try:
        # Vérifier la configuration
        print(f"✅ Configuration chargée: {len(PIPELINE_CONFIG)} paramètres")
        print(f"   - Intervalle collecte: {PIPELINE_CONFIG['data_collection_interval']}s")
        print(f"   - Intervalle prédictions: {PIPELINE_CONFIG['prediction_interval']}s")
        print(f"   - Seuil confiance: {PIPELINE_CONFIG['min_confidence_threshold']}")
        print(f"   - Trades max: {PIPELINE_CONFIG['max_concurrent_trades']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur configuration: {e}")
        return False

def test_pipeline_service():
    """Test du service de pipeline"""
    print("\n🚀 Test du service de pipeline...")
    
    try:
        # Vérifier le statut initial
        status = trading_pipeline_service.get_pipeline_status()
        print(f"✅ Statut initial: {status['is_running']}")
        
        # Vérifier la configuration
        config = status.get('config', {})
        print(f"✅ Configuration chargée: {len(config)} paramètres")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur service: {e}")
        return False

def test_pipeline_start_stop():
    """Test du démarrage/arrêt de la pipeline"""
    print("\n🔄 Test démarrage/arrêt...")
    
    try:
        # Démarrer la pipeline
        print("   - Démarrage de la pipeline...")
        success = trading_pipeline_service.start_pipeline()
        
        if success:
            print("   ✅ Pipeline démarrée")
            
            # Attendre un peu
            time.sleep(2)
            
            # Vérifier le statut
            status = trading_pipeline_service.get_pipeline_status()
            print(f"   ✅ Statut après démarrage: {status['is_running']}")
            
            # Arrêter la pipeline
            print("   - Arrêt de la pipeline...")
            success = trading_pipeline_service.stop_pipeline()
            
            if success:
                print("   ✅ Pipeline arrêtée")
                
                # Vérifier le statut final
                status = trading_pipeline_service.get_pipeline_status()
                print(f"   ✅ Statut final: {status['is_running']}")
                
                return True
            else:
                print("   ❌ Erreur lors de l'arrêt")
                return False
        else:
            print("   ❌ Erreur lors du démarrage")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur test start/stop: {e}")
        return False

def test_data_collection():
    """Test de la collecte de données"""
    print("\n📊 Test de la collecte de données...")
    
    try:
        # Forcer la collecte de données
        print("   - Collecte forcée des données...")
        trading_pipeline_service._collect_market_data()
        
        # Vérifier les données collectées
        market_data = trading_pipeline_service.get_market_data()
        print(f"   ✅ Données collectées: {len(market_data)} symboles")
        
        if market_data:
            for symbol, data in list(market_data.items())[:3]:  # Afficher les 3 premiers
                print(f"      - {symbol}: ${data.get('price', 0):.2f}, sentiment: {data.get('news_sentiment', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur collecte données: {e}")
        return False

def test_prediction_generation():
    """Test de la génération de prédictions"""
    print("\n🔮 Test de la génération de prédictions...")
    
    try:
        # Forcer la génération de prédictions
        print("   - Génération forcée des prédictions...")
        trading_pipeline_service._generate_predictions()
        
        # Vérifier les prédictions générées
        predictions = trading_pipeline_service.get_predictions()
        print(f"   ✅ Prédictions générées: {len(predictions)} symboles")
        
        if predictions:
            for symbol, pred in list(predictions.items())[:3]:  # Afficher les 3 premiers
                print(f"      - {symbol}: {pred.get('direction_prob', 0):.2f}, confiance: {pred.get('confidence', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur génération prédictions: {e}")
        return False

def test_signal_generation():
    """Test de la génération de signaux"""
    print("\n📈 Test de la génération de signaux...")
    
    try:
        # Forcer la génération de signaux
        print("   - Génération forcée des signaux...")
        trading_pipeline_service._generate_trading_signals()
        
        # Vérifier les signaux générés
        signals = trading_pipeline_service.get_signals()
        print(f"   ✅ Signaux générés: {len(signals)} symboles")
        
        if signals:
            for symbol, signal in list(signals.items())[:3]:  # Afficher les 3 premiers
                print(f"      - {symbol}: {signal.get('signal_type', 'N/A')}, confiance: {signal.get('confidence', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur génération signaux: {e}")
        return False

def test_trade_execution():
    """Test de l'exécution des trades"""
    print("\n💼 Test de l'exécution des trades...")
    
    try:
        # Forcer l'exécution des trades
        print("   - Exécution forcée des trades...")
        trading_pipeline_service._execute_trades()
        
        # Vérifier les trades exécutés
        trades = trading_pipeline_service.get_trades()
        print(f"   ✅ Trades exécutés: {len(trades)} symboles")
        
        if trades:
            for symbol, trade in list(trades.items())[:3]:  # Afficher les 3 premiers
                print(f"      - {symbol}: {trade.get('signal_type', 'N/A')}, statut: {trade.get('status', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur exécution trades: {e}")
        return False

def test_statistics():
    """Test des statistiques"""
    print("\n📊 Test des statistiques...")
    
    try:
        # Récupérer les statistiques
        status = trading_pipeline_service.get_pipeline_status()
        stats = status.get('stats', {})
        
        print(f"   ✅ Statistiques récupérées:")
        print(f"      - Total signaux: {stats.get('total_signals', 0)}")
        print(f"      - Total trades: {stats.get('total_trades', 0)}")
        print(f"      - Trades réussis: {stats.get('successful_trades', 0)}")
        print(f"      - P&L total: ${stats.get('total_pnl', 0):.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur statistiques: {e}")
        return False

def run_all_tests():
    """Exécute tous les tests"""
    print("🚀 Démarrage des tests de la pipeline de trading unifiée")
    print("=" * 60)
    
    tests = [
        ("Configuration", test_pipeline_configuration),
        ("Service", test_pipeline_service),
        ("Démarrage/Arrêt", test_pipeline_start_stop),
        ("Collecte données", test_data_collection),
        ("Génération prédictions", test_prediction_generation),
        ("Génération signaux", test_signal_generation),
        ("Exécution trades", test_trade_execution),
        ("Statistiques", test_statistics),
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
    print("📋 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n📊 Résultats: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés avec succès !")
        return True
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez les logs ci-dessus.")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Erreur critique: {e}")
        sys.exit(1)
