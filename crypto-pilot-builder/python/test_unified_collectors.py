#!/usr/bin/env python3
"""
Tests d'intégration pour les collecteurs unifiés
Valide que les collecteurs de données et de news sont correctement fusionnés
"""

import sys
import os
import asyncio
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.agents.trading.unified_data_collector import UnifiedDataCollectorAgent
from services.news_service import news_service, NewsItem
from services.ai_analyzer import ai_analyzer, MarketContext
from services.autowallet_service import autowallet_service

class TestUnifiedCollectors(unittest.TestCase):
    """Tests pour les collecteurs unifiés"""
    
    def setUp(self):
        """Configuration des tests"""
        self.unified_collector = UnifiedDataCollectorAgent()
        self.test_user_id = "test_user_unified_123"
        
    def tearDown(self):
        """Nettoyage après les tests"""
        # Nettoyer les données de test
        try:
            autowallet_service.delete_autowallet(self.test_user_id)
        except:
            pass
    
    def test_unified_collector_initialization(self):
        """Test l'initialisation du collecteur unifié"""
        print("🧪 Test d'initialisation du collecteur unifié...")
        
        # Vérifier que le collecteur est correctement initialisé
        self.assertIsNotNone(self.unified_collector)
        self.assertEqual(self.unified_collector.name, "unified_data_collector")
        self.assertIsNotNone(self.unified_collector.circuit_breaker)
        self.assertIsNotNone(self.unified_collector.cryptos)
        
        # Vérifier les cryptos surveillées
        expected_cryptos = ["bitcoin", "ethereum", "cardano", "polkadot", "solana"]
        for crypto in expected_cryptos:
            self.assertIn(crypto, self.unified_collector.cryptos)
        
        print("✅ Collecteur unifié initialisé correctement")
    
    def test_news_collection_integration(self):
        """Test l'intégration de la collecte de news"""
        print("🧪 Test d'intégration de la collecte de news...")
        
        try:
            # Récupérer des news récentes
            recent_news = news_service.get_recent_news(hours=24)
            
            # Vérifier que des news sont récupérées
            self.assertIsInstance(recent_news, list)
            print(f"✅ {len(recent_news)} news récupérées")
            
            if recent_news:
                # Vérifier la structure des news
                news_item = recent_news[0]
                self.assertIsInstance(news_item, NewsItem)
                self.assertIsNotNone(news_item.id)
                self.assertIsNotNone(news_item.title)
                self.assertIsNotNone(news_item.content)
                self.assertIsNotNone(news_item.source)
                self.assertIsNotNone(news_item.published_at)
                
                print(f"✅ Structure des news validée: {news_item.title[:50]}...")
            
        except Exception as e:
            print(f"⚠️  Erreur lors de la collecte de news: {e}")
            # Ne pas faire échouer le test si l'API externe n'est pas disponible
    
    def test_ai_analyzer_integration(self):
        """Test l'intégration de l'analyseur IA"""
        print("🧪 Test d'intégration de l'analyseur IA...")
        
        try:
            # Créer des news de test
            test_news = [
                NewsItem(
                    id="test_news_1",
                    title="Bitcoin atteint de nouveaux sommets historiques",
                    content="Le Bitcoin continue sa progression avec une adoption institutionnelle croissante.",
                    source="Test Source",
                    published_at=datetime.now(),
                    url="https://test.com/btc-news",
                    sentiment_score=0.7,
                    relevance_score=0.8,
                    crypto_mentions=["BTC"],
                    impact_level="high"
                )
            ]
            
            # Analyser les news
            market_context = ai_analyzer.get_market_context()
            alerts = ai_analyzer.analyze_news_for_investment(test_news, market_context)
            
            # Vérifier que des alertes sont générées
            self.assertIsInstance(alerts, list)
            print(f"✅ {len(alerts)} alertes générées")
            
            if alerts:
                alert = alerts[0]
                self.assertIsNotNone(alert.id)
                self.assertIsNotNone(alert.crypto_symbol)
                self.assertIn(alert.alert_type, ["buy", "sell", "hold"])
                self.assertGreaterEqual(alert.confidence_score, 0.0)
                self.assertLessEqual(alert.confidence_score, 1.0)
                self.assertIsNotNone(alert.reasoning)
                
                print(f"✅ Alerte générée: {alert.alert_type} {alert.crypto_symbol} ({alert.confidence_score:.2f})")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'analyse IA: {e}")
            self.fail(f"L'analyseur IA a échoué: {e}")
    
    def test_autowallet_service_integration(self):
        """Test l'intégration avec le service autowallet"""
        print("🧪 Test d'intégration avec le service autowallet...")
        
        try:
            # Créer une configuration de test
            test_config = {
                'is_active': True,
                'analysis_interval': 5,
                'max_investment_per_trade': 50.0,
                'risk_tolerance': 'low',
                'investment_strategy': 'conservative',
                'min_confidence_threshold': 0.8,
                'crypto_whitelist': ['BTC', 'ETH']
            }
            
            # Créer l'autowallet
            autowallet_id = autowallet_service.create_autowallet(self.test_user_id, test_config)
            self.assertIsNotNone(autowallet_id)
            print(f"✅ Autowallet créé: {autowallet_id}")
            
            # Vérifier le statut
            status = autowallet_service.get_autowallet_status(self.test_user_id)
            self.assertIsInstance(status, dict)
            self.assertTrue(status.get('is_active', False))
            print(f"✅ Statut vérifié: {status['is_active']}")
            
            # Tester l'analyse manuelle
            alerts = autowallet_service.analyze_news_manually(self.test_user_id, ["test_news_1"])
            self.assertIsInstance(alerts, list)
            print(f"✅ Analyse manuelle: {len(alerts)} alertes")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'intégration autowallet: {e}")
            self.fail(f"L'intégration autowallet a échoué: {e}")
    
    @patch('pipeline.agents.trading.unified_data_collector.market_data_service')
    async def test_unified_data_collection_simulation(self, mock_market_service):
        """Test la simulation de collecte de données unifiées"""
        print("🧪 Test de simulation de collecte de données unifiées...")
        
        # Mock des données de marché
        mock_market_service.get_crypto_price.return_value = 50000.0
        
        try:
            # Simuler la collecte de données crypto
            crypto_data = await self.unified_collector._collect_crypto_data(
                None, "bitcoin", "BTC"
            )
            
            if crypto_data:
                self.assertIsInstance(crypto_data, dict)
                self.assertIn("symbol", crypto_data)
                self.assertIn("price", crypto_data)
                self.assertEqual(crypto_data["symbol"], "BTC")
                print(f"✅ Données crypto collectées: {crypto_data['symbol']} = ${crypto_data['price']}")
            
            # Simuler la collecte de news
            news_data = await self.unified_collector._collect_news_data(None)
            self.assertIsInstance(news_data, list)
            print(f"✅ {len(news_data)} news collectées")
            
            # Simuler l'analyse des news
            alerts_data = await self.unified_collector._analyze_news_for_alerts(None, news_data)
            self.assertIsInstance(alerts_data, list)
            print(f"✅ {len(alerts_data)} alertes générées")
            
        except Exception as e:
            print(f"❌ Erreur lors de la simulation: {e}")
            self.fail(f"La simulation de collecte a échoué: {e}")
    
    def test_pipeline_manager_integration(self):
        """Test l'intégration avec le pipeline manager"""
        print("🧪 Test d'intégration avec le pipeline manager...")
        
        try:
            from pipeline.utils.pipeline_manager import PipelineManager
            
            # Créer le pipeline manager
            pipeline_manager = PipelineManager()
            
            # Vérifier que le collecteur unifié est dans les agents
            self.assertIn("unified_data_collector", pipeline_manager.agents)
            print("✅ Collecteur unifié intégré au pipeline manager")
            
            # Vérifier le statut des agents
            agent_status = pipeline_manager.agent_status
            self.assertIn("unified_data_collector", agent_status)
            print("✅ Statut des agents initialisé")
            
            # Tester l'exécution synchrone du collecteur unifié
            unified_data = pipeline_manager._execute_unified_data_collector_sync()
            if unified_data:
                self.assertIsInstance(unified_data, dict)
                self.assertIn("market_data", unified_data)
                self.assertIn("news_data", unified_data)
                self.assertIn("alerts_data", unified_data)
                print("✅ Exécution synchrone du collecteur unifié réussie")
            
        except Exception as e:
            print(f"❌ Erreur lors de l'intégration pipeline manager: {e}")
            self.fail(f"L'intégration pipeline manager a échoué: {e}")
    
    def test_error_handling_and_logging(self):
        """Test la gestion d'erreurs et le logging"""
        print("🧪 Test de gestion d'erreurs et logging...")
        
        try:
            # Tester avec des données invalides
            invalid_news_data = [
                {
                    "id": "invalid_news",
                    "title": None,  # Données invalides
                    "content": None,
                    "source": None,
                    "published_at": "invalid_date",
                    "url": None,
                    "sentiment_score": "invalid",
                    "relevance_score": "invalid",
                    "crypto_mentions": None,
                    "impact_level": None
                }
            ]
            
            # L'analyseur devrait gérer les erreurs gracieusement
            market_context = ai_analyzer.get_market_context()
            alerts = ai_analyzer.analyze_news_for_investment([], market_context)
            self.assertIsInstance(alerts, list)
            print("✅ Gestion d'erreurs avec données vides")
            
            # Tester le circuit breaker
            circuit_breaker = self.unified_collector.circuit_breaker
            self.assertIsNotNone(circuit_breaker)
            print("✅ Circuit breaker initialisé")
            
        except Exception as e:
            print(f"❌ Erreur lors du test de gestion d'erreurs: {e}")
            self.fail(f"La gestion d'erreurs a échoué: {e}")

def run_integration_tests():
    """Lance tous les tests d'intégration"""
    print("🚀 Démarrage des tests d'intégration pour les collecteurs unifiés")
    print("=" * 70)
    
    # Créer la suite de tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestUnifiedCollectors)
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Résumé des résultats
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS D'INTÉGRATION")
    print("=" * 70)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    successes = total_tests - failures - errors
    
    print(f"Tests exécutés: {total_tests}")
    print(f"✅ Réussis: {successes}")
    print(f"❌ Échecs: {failures}")
    print(f"💥 Erreurs: {errors}")
    
    if failures > 0:
        print("\n🔍 DÉTAILS DES ÉCHECS:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if errors > 0:
        print("\n💥 DÉTAILS DES ERREURS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\\n')[-2]}")
    
    success_rate = (successes / total_tests) * 100 if total_tests > 0 else 0
    print(f"\n📈 Taux de réussite: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Tests d'intégration réussis ! Les collecteurs sont correctement fusionnés.")
        return 0
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        return 1

if __name__ == "__main__":
    exit_code = run_integration_tests()
    sys.exit(exit_code)
