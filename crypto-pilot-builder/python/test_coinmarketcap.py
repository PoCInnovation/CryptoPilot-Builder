#!/usr/bin/env python3
"""
Script de test pour l'API CoinMarketCap
"""

import os
import requests
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

def test_coinmarketcap_api():
    """Test de l'API CoinMarketCap"""
    api_key = os.getenv('COINMARKETCAP_API_KEY')
    
    if not api_key:
        print("❌ Clé API CoinMarketCap non configurée")
        print("   Ajoutez COINMARKETCAP_API_KEY=your_key dans votre fichier .env")
        return False
    
    print("🔑 Clé API CoinMarketCap trouvée")
    
    # Test de l'endpoint news
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/news"
    headers = {
        'X-CMC_PRO_API_KEY': api_key,
        'Accept': 'application/json'
    }
    params = {
        'limit': 5,
        'sort': 'published_at',
        'sort_dir': 'desc'
    }
    
    try:
        print("📡 Test de l'endpoint news...")
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API fonctionne ! {len(data.get('data', []))} news récupérées")
            
            # Afficher les premières news
            if 'data' in data and data['data']:
                print("\n📰 Premières news:")
                for i, news in enumerate(data['data'][:3]):
                    print(f"\n{i+1}. {news.get('title', 'Sans titre')}")
                    print(f"   Source: {news.get('source', 'Inconnue')}")
                    print(f"   Date: {news.get('published_at', 'Inconnue')}")
                    print(f"   URL: {news.get('url', 'Non disponible')}")
                    
                    # Afficher les cryptomonnaies mentionnées
                    if 'currencies' in news:
                        symbols = [c.get('symbol', '') for c in news['currencies'] if c.get('symbol')]
                        if symbols:
                            print(f"   Cryptos: {', '.join(symbols)}")
            
            return True
        else:
            print(f"❌ Erreur API: {response.status_code}")
            print(f"   Réponse: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def test_news_service():
    """Test du service de news avec l'API CoinMarketCap"""
    print("\n🧪 Test du service de news...")
    
    try:
        from services.news_service import news_service
        
        # Récupérer les news
        news = news_service.fetch_crypto_news(limit=5)
        print(f"✅ {len(news)} news récupérées par le service")
        
        if news:
            print("\n📊 Analyse des news:")
            for i, n in enumerate(news[:3]):
                print(f"\n{i+1}. {n.title}")
                print(f"   Source: {n.source}")
                print(f"   Date: {n.published_at}")
                print(f"   Cryptos: {n.crypto_mentions}")
                print(f"   Sentiment: {n.sentiment_score:.2f}")
                print(f"   Pertinence: {n.relevance_score:.2f}")
                print(f"   Impact: {n.impact_level}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans le service de news: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Test de l'API CoinMarketCap")
    print("=" * 50)
    
    # Test de l'API
    api_ok = test_coinmarketcap_api()
    
    if api_ok:
        # Test du service
        service_ok = test_news_service()
        
        if service_ok:
            print("\n🎉 Tous les tests sont passés !")
            print("   L'API CoinMarketCap est configurée et fonctionne correctement.")
        else:
            print("\n⚠️  L'API fonctionne mais le service a des problèmes.")
    else:
        print("\n❌ L'API CoinMarketCap n'est pas accessible.")
        print("   Vérifiez votre clé API et votre connexion internet.")
