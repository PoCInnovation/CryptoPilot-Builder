#!/usr/bin/env python3
"""
Script de debug pour les news
"""

from services.news_service import news_service
from services.ai_analyzer import ai_analyzer

def debug_news():
    print("🔍 Debug des news...")
    
    # Récupérer les news
    news = news_service.get_recent_news(24)
    print(f"📰 {len(news)} news récupérées")
    
    if not news:
        print("❌ Aucune news récupérée")
        return
    
    # Analyser les premières news
    print("\n📊 Analyse des news:")
    for i, n in enumerate(news[:3]):
        print(f"\n{i+1}. {n.title}")
        print(f"   Sentiment: {n.sentiment_score:.2f}")
        print(f"   Pertinence: {n.relevance_score:.2f}")
        print(f"   Impact: {n.impact_level}")
        print(f"   Cryptos: {n.crypto_mentions}")
    
    # Tester l'analyseur IA
    print("\n🧠 Test de l'analyseur IA...")
    alerts = ai_analyzer.analyze_news_for_investment(news[:3])
    print(f"🚨 {len(alerts)} alertes générées")
    
    if alerts:
        for i, alert in enumerate(alerts):
            print(f"\n{i+1}. Alerte {alert.alert_type.upper()} pour {alert.crypto_symbol}")
            print(f"   Confiance: {alert.confidence_score:.2f}")
            print(f"   Raisonnement: {alert.reasoning[:100]}...")
    else:
        print("❌ Aucune alerte générée")
        print("   Vérifiez les seuils de confiance et d'impact")

if __name__ == "__main__":
    debug_news()
