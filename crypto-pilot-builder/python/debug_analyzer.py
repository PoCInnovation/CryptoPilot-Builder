#!/usr/bin/env python3
"""
Script de debug pour l'analyseur IA et la génération de trades
"""

from services.news_service import news_service
from services.ai_analyzer import ai_analyzer
import json

def debug_analyzer():
    """Debug de l'analyseur IA"""
    print("🧠 Debug de l'analyseur IA")
    print("=" * 50)
    
    # Récupérer les news
    news = news_service.get_recent_news(5)
    print(f"📰 {len(news)} news récupérées")
    
    if not news:
        print("❌ Aucune news récupérée")
        return
    
    # Analyser chaque news individuellement
    print("\n📊 Analyse détaillée des news:")
    for i, n in enumerate(news[:3]):
        print(f"\n{i+1}. {n.title}")
        print(f"   Sentiment: {n.sentiment_score:.3f}")
        print(f"   Pertinence: {n.relevance_score:.3f}")
        print(f"   Impact: {n.impact_level}")
        print(f"   Cryptos: {n.crypto_mentions}")
        
        # Analyser cette news spécifique
        analysis = ai_analyzer._analyze_single_news(n, None)
        if analysis:
            print(f"   → Action: {analysis.action.upper()}")
            print(f"   → Confiance: {analysis.confidence:.3f}")
            print(f"   → Raisonnement: {analysis.reasoning[:100]}...")
        else:
            print("   → ❌ Analyse échouée")
    
    # Test de l'analyseur complet
    print("\n🚨 Test de l'analyseur complet:")
    alerts = ai_analyzer.analyze_news_for_investment(news)
    print(f"✅ {len(alerts)} alertes générées")
    
    if alerts:
        for i, alert in enumerate(alerts):
            print(f"\n{i+1}. Alerte {alert.alert_type.upper()} pour {alert.crypto_symbol}")
            print(f"   Confiance: {alert.confidence_score:.3f}")
            print(f"   Raisonnement: {alert.reasoning[:100]}...")
            print(f"   Priorité: {alert.priority}")
            print(f"   Créé le: {alert.created_at}")
    else:
        print("❌ Aucune alerte générée")
        print("\n🔍 Vérification des seuils:")
        print(f"   Seuil de confiance: {ai_analyzer.confidence_threshold}")
        print("   Seuils d'impact requis: high, critical")
    
    return alerts

def debug_trade_generation():
    """Debug de la génération de trades"""
    print("\n💰 Debug de la génération de trades")
    print("=" * 50)
    
    try:
        from services.autowallet_service import autowallet_service
        
        # Créer un autowallet de test
        user_id = "test_user_debug"
        config = {
            "user_id": user_id,
            "max_investment": 1000.0,
            "risk_tolerance": "medium",
            "strategy": "balanced",
            "confidence_threshold": 0.6,
            "crypto_whitelist": ["BTC", "ETH", "ADA", "SOL", "DOT"]
        }
        
        print("🔧 Création d'un autowallet de test...")
        autowallet_id = autowallet_service.create_autowallet(user_id, config)
        print(f"✅ Autowallet créé: {autowallet_id}")
        
        # Récupérer les news et analyser
        news = news_service.get_recent_news(10)
        alerts = ai_analyzer.analyze_news_for_investment(news)
        
        print(f"\n📊 {len(alerts)} alertes disponibles pour génération de trades")
        
        # Simuler la génération de trades
        for alert in alerts[:3]:
            if alert.confidence_score >= 0.6:  # Seuil de confiance
                print(f"\n💡 Alerte qualifiée: {alert.alert_type.upper()} {alert.crypto_symbol}")
                print(f"   Confiance: {alert.confidence_score:.3f}")
                print(f"   Action recommandée: {alert.alert_type}")
                
                # Vérifier si un trade serait créé
                if alert.alert_type in ["buy", "sell"]:
                    print("   ✅ Trade potentiel détecté")
                else:
                    print("   ⏸️  Action 'hold' - pas de trade")
        
        # Nettoyer
        autowallet_service.delete_autowallet(user_id)
        print(f"\n🧹 Autowallet de test supprimé")
        
    except Exception as e:
        print(f"❌ Erreur lors du debug des trades: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Debug complet de l'analyseur IA et des trades")
    print("=" * 60)
    
    # Debug de l'analyseur
    alerts = debug_analyzer()
    
    # Debug des trades
    debug_trade_generation()
    
    print("\n📋 Résumé:")
    if alerts:
        print(f"✅ {len(alerts)} alertes générées")
        print("   Vérifiez que les alertes ont une confiance suffisante")
        print("   et que l'action n'est pas 'hold'")
    else:
        print("❌ Aucune alerte générée")
        print("   Vérifiez les seuils de confiance et d'impact")
