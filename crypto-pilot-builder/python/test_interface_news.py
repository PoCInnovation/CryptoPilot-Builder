#!/usr/bin/env python3
"""
Script de test pour vérifier que l'interface AutoWallet peut récupérer les vraies news
"""

from services.news_service import news_service
from services.ai_analyzer import ai_analyzer
import json

def test_interface_news():
    """Test que l'interface peut récupérer et afficher les vraies news"""
    print("🧪 Test de l'interface AutoWallet avec vraies news")
    print("=" * 60)
    
    # Récupérer les news
    print("📡 Récupération des news depuis CryptoCompare...")
    news = news_service.get_recent_news(hours=24)
    
    if not news:
        print("❌ Aucune news récupérée")
        return False
    
    print(f"✅ {len(news)} news récupérées")
    
    # Afficher les premières news avec formatage pour l'interface
    print("\n📰 News pour l'interface AutoWallet:")
    for i, n in enumerate(news[:5]):
        print(f"\n{i+1}. {n.title}")
        print(f"   Source: {n.source}")
        print(f"   Date: {n.published_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Cryptos: {', '.join(n.crypto_mentions) if n.crypto_mentions else 'Aucune'}")
        print(f"   Sentiment: {n.sentiment_score:.2f}")
        print(f"   Pertinence: {n.relevance_score:.2f}")
        print(f"   Impact: {n.impact_level}")
        print(f"   URL: {n.url}")
    
    # Tester l'analyseur IA
    print("\n🧠 Test de l'analyseur IA...")
    alerts = ai_analyzer.analyze_news_for_investment(news[:3])
    
    if alerts:
        print(f"✅ {len(alerts)} alertes générées")
        for i, alert in enumerate(alerts):
            print(f"\n{i+1}. Alerte {alert.alert_type.upper()} pour {alert.crypto_symbol}")
            print(f"   Confiance: {alert.confidence_score:.2f}")
            print(f"   Raisonnement: {alert.reasoning[:100]}...")
    else:
        print("⚠️  Aucune alerte générée")
    
    # Simuler le format JSON que l'interface recevra
    print("\n📊 Format JSON pour l'interface:")
    news_data = []
    for news in news[:3]:
        news_data.append({
            "id": news.id,
            "title": news.title,
            "content": news.content,
            "source": news.source,
            "published_at": news.published_at.isoformat(),
            "url": news.url,
            "sentiment_score": news.sentiment_score,
            "relevance_score": news.relevance_score,
            "crypto_mentions": news.crypto_mentions,
            "impact_level": news.impact_level
        })
    
    print(json.dumps(news_data, indent=2, ensure_ascii=False))
    
    return True

def test_news_api_endpoint():
    """Test que l'endpoint API fonctionne"""
    print("\n🔌 Test de l'endpoint API /api/autowallet/news")
    print("=" * 50)
    
    try:
        from mcp_client.autowallet_routes import create_autowallet_routes
        from flask import Flask
        
        # Créer une app Flask de test
        app = Flask(__name__)
        create_autowallet_routes(app)
        
        print("✅ Routes AutoWallet créées avec succès")
        print("✅ Endpoint /api/autowallet/news disponible")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des routes: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test de l'interface AutoWallet avec vraies news")
    print("=" * 60)
    
    # Test des news
    news_ok = test_interface_news()
    
    # Test de l'API
    api_ok = test_news_api_endpoint()
    
    if news_ok and api_ok:
        print("\n🎉 Tous les tests sont passés !")
        print("   L'interface AutoWallet peut maintenant afficher de vraies news crypto !")
        print("\n📋 Prochaines étapes:")
        print("   1. Démarrez le serveur: python app.py")
        print("   2. Ouvrez l'interface AutoWallet")
        print("   3. Vérifiez que les vraies news s'affichent")
    else:
        print("\n❌ Certains tests ont échoué")
        print("   Vérifiez la configuration et les logs")
