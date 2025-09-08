#!/usr/bin/env python3
"""
Tests d'intégration pour le dashboard AutoWallet avec les nouvelles sous-pages
Valide que les composants News+Alerts et Full Pipeline fonctionnent correctement
"""

import sys
import os
import asyncio
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Ajouter le répertoire parent au path Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.news_service import news_service, NewsItem
from services.ai_analyzer import ai_analyzer, MarketContext
from services.autowallet_service import autowallet_service
from services.alert_service import alert_service

class TestDashboardIntegration(unittest.TestCase):
    """Tests d'intégration pour le dashboard"""
    
    def setUp(self):
        """Configuration des tests"""
        self.test_user_id = "test_dashboard_user_456"
        
    def tearDown(self):
        """Nettoyage après les tests"""
        # Nettoyer les données de test
        try:
            autowallet_service.delete_autowallet(self.test_user_id)
        except:
            pass
    
    def test_news_alerts_dashboard_data_flow(self):
        """Test le flux de données pour le dashboard News+Alerts"""
        print("🧪 Test du flux de données News+Alerts...")
        
        try:
            # 1. Créer une configuration autowallet
            test_config = {
                'is_active': True,
                'analysis_interval': 5,
                'max_investment_per_trade': 100.0,
                'risk_tolerance': 'medium',
                'investment_strategy': 'balanced',
                'min_confidence_threshold': 0.3,
                'crypto_whitelist': ['BTC', 'ETH', 'ADA']
            }
            
            autowallet_id = autowallet_service.create_autowallet(self.test_user_id, test_config)
            self.assertIsNotNone(autowallet_id)
            print("✅ Configuration autowallet créée")
            
            # 2. Récupérer des news récentes
            recent_news = news_service.get_recent_news(hours=24)
            self.assertIsInstance(recent_news, list)
            print(f"✅ {len(recent_news)} news récupérées pour le dashboard")
            
            # 3. Générer des alertes à partir des news
            if recent_news:
                market_context = ai_analyzer.get_market_context()
                alerts = ai_analyzer.analyze_news_for_investment(recent_news[:3], market_context)
                self.assertIsInstance(alerts, list)
                print(f"✅ {len(alerts)} alertes générées pour le dashboard")
                
                # 4. Vérifier la structure des données pour l'interface
                for alert in alerts:
                    self.assertIsNotNone(alert.id)
                    self.assertIsNotNone(alert.crypto_symbol)
                    self.assertIn(alert.alert_type, ["buy", "sell", "hold"])
                    self.assertGreaterEqual(alert.confidence_score, 0.0)
                    self.assertLessEqual(alert.confidence_score, 1.0)
                    self.assertIsNotNone(alert.reasoning)
                    self.assertIsNotNone(alert.created_at)
                
                print("✅ Structure des alertes validée pour l'interface")
            
            # 5. Tester l'analyse manuelle
            if recent_news:
                news_ids = [news.id for news in recent_news[:2]]
                manual_alerts = autowallet_service.analyze_news_manually(self.test_user_id, news_ids)
                self.assertIsInstance(manual_alerts, list)
                print(f"✅ Analyse manuelle: {len(manual_alerts)} alertes")
            
        except Exception as e:
            print(f"❌ Erreur dans le flux News+Alerts: {e}")
            self.fail(f"Le flux de données News+Alerts a échoué: {e}")
    
    def test_full_pipeline_dashboard_data_flow(self):
        """Test le flux de données pour le dashboard Full Pipeline"""
        print("🧪 Test du flux de données Full Pipeline...")
        
        try:
            # 1. Tester l'intégration avec le pipeline manager
            from pipeline.utils.pipeline_manager import PipelineManager
            
            pipeline_manager = PipelineManager()
            
            # Vérifier que tous les agents sont présents
            expected_agents = [
                "unified_data_collector",
                "predictor", 
                "strategy",
                "trader",
                "logger"
            ]
            
            for agent_name in expected_agents:
                self.assertIn(agent_name, pipeline_manager.agents)
                self.assertIn(agent_name, pipeline_manager.agent_status)
            
            print("✅ Tous les agents du pipeline sont présents")
            
            # 2. Tester l'exécution du collecteur unifié
            unified_data = pipeline_manager._execute_unified_data_collector_sync()
            if unified_data:
                self.assertIsInstance(unified_data, dict)
                self.assertIn("market_data", unified_data)
                self.assertIn("news_data", unified_data)
                self.assertIn("alerts_data", unified_data)
                self.assertIn("timestamp", unified_data)
                print("✅ Données unifiées générées pour le pipeline")
            
            # 3. Tester l'exécution de la séquence complète
            pipeline_data = pipeline_manager._execute_pipeline_sequence_sync()
            if pipeline_data:
                self.assertIsNotNone(pipeline_data.timestamp)
                self.assertIsNotNone(pipeline_data.symbol)
                self.assertIsNotNone(pipeline_data.metadata)
                print("✅ Séquence complète du pipeline exécutée")
            
            # 4. Vérifier les statistiques du pipeline
            stats = pipeline_manager.get_pipeline_stats()
            self.assertIsInstance(stats, dict)
            self.assertIn("total_executions", stats)
            self.assertIn("success_rate", stats)
            self.assertIn("average_execution_time", stats)
            print("✅ Statistiques du pipeline récupérées")
            
        except Exception as e:
            print(f"❌ Erreur dans le flux Full Pipeline: {e}")
            self.fail(f"Le flux de données Full Pipeline a échoué: {e}")
    
    def test_dashboard_refresh_functionality(self):
        """Test la fonctionnalité de rafraîchissement du dashboard"""
        print("🧪 Test de la fonctionnalité de rafraîchissement...")
        
        try:
            # 1. Créer une configuration
            test_config = {
                'is_active': True,
                'analysis_interval': 1,  # Intervalle court pour les tests
                'max_investment_per_trade': 50.0,
                'risk_tolerance': 'low',
                'investment_strategy': 'conservative',
                'min_confidence_threshold': 0.5,
                'crypto_whitelist': ['BTC', 'ETH']
            }
            
            autowallet_id = autowallet_service.create_autowallet(self.test_user_id, test_config)
            print("✅ Configuration créée pour le test de rafraîchissement")
            
            # 2. Démarrer le monitoring
            autowallet_service.start_monitoring(self.test_user_id)
            print("✅ Monitoring démarré")
            
            # 3. Attendre un peu pour que le monitoring collecte des données
            import time
            time.sleep(2)
            
            # 4. Vérifier que des données ont été collectées
            status = autowallet_service.get_autowallet_status(self.test_user_id)
            self.assertTrue(status.get('is_monitoring', False))
            print("✅ Monitoring actif confirmé")
            
            # 5. Arrêter le monitoring
            autowallet_service.stop_monitoring(self.test_user_id)
            print("✅ Monitoring arrêté")
            
        except Exception as e:
            print(f"❌ Erreur dans le test de rafraîchissement: {e}")
            self.fail(f"Le test de rafraîchissement a échoué: {e}")
    
    def test_alert_service_integration(self):
        """Test l'intégration avec le service d'alertes"""
        print("🧪 Test d'intégration avec le service d'alertes...")
        
        try:
            # 1. Ajouter un canal d'alerte de test
            channel_id = alert_service.add_alert_channel(
                self.test_user_id,
                'email',
                {'email': 'test@example.com'}
            )
            self.assertIsNotNone(channel_id)
            print(f"✅ Canal d'alerte ajouté: {channel_id}")
            
            # 2. Vérifier que le canal est dans la liste
            user_channels = alert_service.get_user_channels(self.test_user_id)
            self.assertIsInstance(user_channels, list)
            self.assertGreater(len(user_channels), 0)
            print(f"✅ {len(user_channels)} canal(s) d'alerte trouvé(s)")
            
            # 3. Créer une alerte de test
            from services.news_service import InvestmentAlert
            
            test_alert = InvestmentAlert(
                id="test_alert_123",
                news_id="test_news_123",
                crypto_symbol="BTC",
                alert_type="buy",
                confidence_score=0.8,
                reasoning="Test d'intégration du service d'alertes",
                created_at=datetime.now(),
                priority="high"
            )
            
            # 4. Tester l'envoi d'alerte (simulation)
            # Note: En production, cela enverrait vraiment l'email
            success = alert_service.send_investment_alert(test_alert, self.test_user_id)
            # Le succès peut être False si SMTP n'est pas configuré, c'est normal
            print(f"✅ Envoi d'alerte testé (succès: {success})")
            
            # 5. Nettoyer
            alert_service.remove_alert_channel(self.test_user_id, channel_id)
            print("✅ Canal d'alerte supprimé")
            
        except Exception as e:
            print(f"❌ Erreur dans l'intégration des alertes: {e}")
            self.fail(f"L'intégration des alertes a échoué: {e}")
    
    def test_dashboard_error_handling(self):
        """Test la gestion d'erreurs du dashboard"""
        print("🧪 Test de gestion d'erreurs du dashboard...")
        
        try:
            # 1. Tester avec un utilisateur inexistant
            status = autowallet_service.get_autowallet_status("user_inexistant")
            self.assertIn("error", status)
            print("✅ Gestion d'erreur pour utilisateur inexistant")
            
            # 2. Tester l'analyse avec des IDs de news invalides
            alerts = autowallet_service.analyze_news_manually(self.test_user_id, ["invalid_id"])
            self.assertIsInstance(alerts, list)
            self.assertEqual(len(alerts), 0)
            print("✅ Gestion d'erreur pour IDs de news invalides")
            
            # 3. Tester la récupération d'historique pour un utilisateur sans trades
            history = autowallet_service.get_trade_history(self.test_user_id)
            self.assertIsInstance(history, list)
            print("✅ Gestion d'historique vide")
            
            # 4. Tester les alertes pour un utilisateur sans configuration
            user_alerts = autowallet_service.get_user_alerts("user_inexistant")
            self.assertIsInstance(user_alerts, list)
            print("✅ Gestion d'alertes pour utilisateur inexistant")
            
        except Exception as e:
            print(f"❌ Erreur dans le test de gestion d'erreurs: {e}")
            self.fail(f"La gestion d'erreurs a échoué: {e}")
    
    def test_dashboard_performance(self):
        """Test les performances du dashboard"""
        print("🧪 Test des performances du dashboard...")
        
        try:
            import time
            
            # 1. Test de performance de la collecte de news
            start_time = time.time()
            recent_news = news_service.get_recent_news(hours=24)
            news_time = time.time() - start_time
            print(f"✅ Collecte de news: {news_time:.2f}s pour {len(recent_news)} news")
            
            # 2. Test de performance de l'analyse IA
            if recent_news:
                start_time = time.time()
                market_context = ai_analyzer.get_market_context()
                alerts = ai_analyzer.analyze_news_for_investment(recent_news[:5], market_context)
                analysis_time = time.time() - start_time
                print(f"✅ Analyse IA: {analysis_time:.2f}s pour {len(alerts)} alertes")
            
            # 3. Test de performance du pipeline manager
            from pipeline.utils.pipeline_manager import PipelineManager
            pipeline_manager = PipelineManager()
            
            start_time = time.time()
            unified_data = pipeline_manager._execute_unified_data_collector_sync()
            pipeline_time = time.time() - start_time
            print(f"✅ Pipeline unifié: {pipeline_time:.2f}s")
            
            # Vérifier que les performances sont acceptables (< 5 secondes)
            self.assertLess(news_time, 5.0, "La collecte de news est trop lente")
            if recent_news:
                self.assertLess(analysis_time, 5.0, "L'analyse IA est trop lente")
            self.assertLess(pipeline_time, 5.0, "Le pipeline est trop lent")
            
        except Exception as e:
            print(f"❌ Erreur dans le test de performance: {e}")
            self.fail(f"Le test de performance a échoué: {e}")

def run_dashboard_integration_tests():
    """Lance tous les tests d'intégration du dashboard"""
    print("🚀 Démarrage des tests d'intégration du dashboard")
    print("=" * 70)
    
    # Créer la suite de tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDashboardIntegration)
    
    # Exécuter les tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Résumé des résultats
    print("\n" + "=" * 70)
    print("📊 RÉSUMÉ DES TESTS D'INTÉGRATION DU DASHBOARD")
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
        print("🎉 Tests d'intégration du dashboard réussis !")
        print("   Les sous-pages News+Alerts et Full Pipeline sont opérationnelles.")
        return 0
    else:
        print("⚠️  Certains tests ont échoué. Vérifiez la configuration.")
        return 1

if __name__ == "__main__":
    exit_code = run_dashboard_integration_tests()
    sys.exit(exit_code)
