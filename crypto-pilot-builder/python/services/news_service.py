#!/usr/bin/env python3
"""
Service de news crypto pour l'autowallet
Analyse les actualités et détecte les opportunités d'investissement
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class NewsItem:
    """Représente un article de news"""
    id: str
    title: str
    content: str
    source: str
    published_at: datetime
    url: str
    sentiment_score: float = 0.0
    relevance_score: float = 0.0
    crypto_mentions: List[str] = None
    impact_level: str = "low"  # low, medium, high, critical

@dataclass
class InvestmentAlert:
    """Représente une alerte d'investissement"""
    id: str
    news_id: str
    crypto_symbol: str
    alert_type: str  # buy, sell, hold
    confidence_score: float
    reasoning: str
    created_at: datetime
    priority: str = "medium"  # low, medium, high, urgent

class NewsService:
    """Service de gestion des news crypto"""
    
    def __init__(self):
        # Utilisation de l'API CryptoCompare (même que le Bento)
        self.base_url = "https://min-api.cryptocompare.com/data/v2"
        self.cache_duration = timedelta(minutes=15)
        self.last_fetch = None
        self.cached_news = []
        
    def fetch_crypto_news(self, limit: int = 50) -> List[NewsItem]:
        """Récupère les dernières news crypto depuis CryptoCompare (même API que le Bento)"""
        try:
            # Endpoint pour les news de CryptoCompare
            url = f"{self.base_url}/news/?lang=EN&limit={min(limit, 50)}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                news_items = self._parse_cryptocompare_news(data)
                self.cached_news = news_items
                self.last_fetch = datetime.now()
                logger.info(f"✅ {len(news_items)} news récupérées depuis CryptoCompare")
                return news_items
            else:
                logger.error(f"Erreur API CryptoCompare: {response.status_code} - {response.text}")
                # Fallback vers les news simulées
                return self._get_fallback_news(limit)
                
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des news: {e}")
            return self._get_fallback_news(limit)
    
    def _parse_cryptocompare_news(self, data: Dict) -> List[NewsItem]:
        """Parse les données de l'API CryptoCompare (même format que le Bento)"""
        news_items = []
        
        try:
            if 'Data' in data and isinstance(data['Data'], list):
                for item in data['Data']:
                    # Extraire les cryptomonnaies mentionnées depuis les catégories et le titre
                    crypto_mentions = []
                    
                    # D'abord, essayer de détecter les cryptomonnaies dans le titre et le contenu
                    title_content = (item.get('title', '') + ' ' + item.get('body', '')).upper()
                    crypto_mentions = self._extract_crypto_mentions(title_content)
                    
                    # Si aucune crypto n'est trouvée, essayer les catégories
                    if not crypto_mentions and 'categories' in item and item['categories']:
                        categories = item['categories'].split('|') if isinstance(item['categories'], str) else [item['categories']]
                        for category in categories:
                            category = category.strip()
                            if category and category not in ['GENERAL', 'TECHNOLOGY', 'BUSINESS', 'POLITICS', 'CRYPTOCURRENCY', 'BLOCKCHAIN', 'TRADING', 'MARKET', 'FIAT']:
                                # Essayer d'extraire des symboles de crypto des catégories
                                extracted = self._extract_crypto_mentions(category)
                                if extracted:
                                    crypto_mentions.extend(extracted)
                    
                    # Parser la date de publication (timestamp Unix)
                    published_at = datetime.now()
                    if 'published_on' in item:
                        try:
                            published_at = datetime.fromtimestamp(item['published_on'])
                        except:
                            published_at = datetime.now()
                    
                    news_item = NewsItem(
                        id=str(item.get('id', hash(item.get('title', '')))),
                        title=item.get('title', ''),
                        content=item.get('body', ''),
                        source=item.get('source_info', {}).get('name', 'CryptoCompare') if item.get('source_info') else 'CryptoCompare',
                        published_at=published_at,
                        url=item.get('url', ''),
                        crypto_mentions=crypto_mentions
                    )
                    news_items.append(news_item)
                    
        except Exception as e:
            logger.error(f"Erreur lors du parsing des news CryptoCompare: {e}")
        
        return news_items
    
    def _get_fallback_news(self, limit: int) -> List[NewsItem]:
        """Génère des news simulées en cas d'échec de l'API"""
        fallback_news = [
            {
                'id': 'fallback_1',
                'title': 'Bitcoin atteint de nouveaux sommets historiques',
                'content': 'Le Bitcoin continue sa progression avec une adoption institutionnelle croissante et une adoption dans les pays en développement.',
                'source': 'CryptoNews Simulé',
                'published_at': datetime.now() - timedelta(hours=2),
                'url': 'https://example.com/btc-news',
                'crypto_mentions': ['BTC']
            },
            {
                'id': 'fallback_2',
                'title': 'Ethereum 2.0 montre des signes de progression',
                'content': 'La transition vers la preuve d\'enjeu progresse bien avec des améliorations de performance notables.',
                'source': 'CryptoNews Simulé',
                'published_at': datetime.now() - timedelta(hours=4),
                'url': 'https://example.com/eth-news',
                'crypto_mentions': ['ETH']
            },
            {
                'id': 'fallback_3',
                'title': 'Cardano annonce de nouveaux partenariats',
                'content': 'Cardano étend son écosystème avec de nouveaux partenariats stratégiques en Afrique.',
                'source': 'CryptoNews Simulé',
                'published_at': datetime.now() - timedelta(hours=6),
                'url': 'https://example.com/ada-news',
                'crypto_mentions': ['ADA']
            },
            {
                'id': 'fallback_4',
                'title': 'Solana améliore ses performances réseau',
                'content': 'Solana annonce des améliorations significatives de sa vitesse de transaction et de sa stabilité.',
                'source': 'CryptoNews Simulé',
                'published_at': datetime.now() - timedelta(hours=8),
                'url': 'https://example.com/sol-news',
                'crypto_mentions': ['SOL']
            },
            {
                'id': 'fallback_5',
                'title': 'Polkadot lance de nouveaux parachains',
                'content': 'L\'écosystème Polkadot continue de s\'étendre avec le lancement de nouveaux parachains spécialisés.',
                'source': 'CryptoNews Simulé',
                'published_at': datetime.now() - timedelta(hours=10),
                'url': 'https://example.com/dot-news',
                'crypto_mentions': ['DOT']
            }
        ]
        
        # Convertir en NewsItem
        news_items = []
        for item in fallback_news[:limit]:
            news_item = NewsItem(
                id=item['id'],
                title=item['title'],
                content=item['content'],
                source=item['source'],
                published_at=item['published_at'],
                url=item['url'],
                crypto_mentions=item['crypto_mentions']
            )
            news_items.append(news_item)
        
        return news_items
    
    def _extract_crypto_mentions(self, text: str) -> List[str]:
        """Extrait les mentions de cryptomonnaies du texte"""
        crypto_symbols = [
            'BTC', 'ETH', 'ADA', 'DOT', 'SOL', 'MATIC', 'AVAX', 'UNI', 'LINK',
            'BNB', 'XRP', 'DOGE', 'SHIB', 'LTC', 'BCH', 'XLM', 'VET', 'TRX',
            'ATOM', 'NEAR', 'FTM', 'ALGO', 'ICP', 'FIL', 'THETA', 'EOS', 'AAVE'
        ]
        
        mentions = []
        text_upper = text.upper()
        
        for symbol in crypto_symbols:
            if symbol in text_upper:
                mentions.append(symbol)
        
        return mentions
    
    def analyze_sentiment(self, news_item: NewsItem) -> float:
        """Analyse le sentiment d'un article (basique)"""
        positive_words = [
            'bullish', 'moon', 'pump', 'surge', 'rally', 'breakout', 'adoption',
            'partnership', 'upgrade', 'innovation', 'growth', 'profit', 'gain',
            'success', 'launch', 'integration', 'expansion', 'milestone', 'achievement'
        ]
        
        negative_words = [
            'bearish', 'crash', 'dump', 'sell-off', 'decline', 'bear market',
            'regulation', 'ban', 'hack', 'scam', 'loss', 'bankruptcy', 'failure',
            'delay', 'issue', 'problem', 'concern', 'risk', 'volatility'
        ]
        
        text = (news_item.title + ' ' + news_item.content).lower()
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.0
        
        sentiment = (positive_count - negative_count) / total_words
        return max(-1.0, min(1.0, sentiment * 15))  # Normaliser entre -1 et 1
    
    def calculate_relevance(self, news_item: NewsItem) -> float:
        """Calcule la pertinence d'une news pour l'investissement"""
        relevance_score = 0.0
        
        # Score basé sur la fraîcheur
        hours_old = (datetime.now() - news_item.published_at).total_seconds() / 3600
        if hours_old < 1:
            relevance_score += 0.4
        elif hours_old < 6:
            relevance_score += 0.3
        elif hours_old < 24:
            relevance_score += 0.2
        elif hours_old < 48:
            relevance_score += 0.1
        
        # Score basé sur les mentions de crypto
        if news_item.crypto_mentions:
            relevance_score += 0.3
        
        # Score basé sur la source (priorité aux sources fiables)
        trusted_sources = ['coindesk', 'cointelegraph', 'bitcoin.com', 'decrypt', 'reuters', 'bloomberg']
        if any(source in news_item.source.lower() for source in trusted_sources):
            relevance_score += 0.2
        
        # Score basé sur le contenu (longueur, mots-clés)
        content_length = len(news_item.content)
        if content_length > 200:
            relevance_score += 0.1
        
        return min(1.0, relevance_score)
    
    def get_recent_news(self, hours: int = 24) -> List[NewsItem]:
        """Récupère les news récentes"""
        # Si pas de cache ou cache expiré, récupérer de nouvelles news
        if not self.cached_news or not self.last_fetch or datetime.now() - self.last_fetch > self.cache_duration:
            self.fetch_crypto_news()
        
        if not self.cached_news:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_news = [
            news for news in self.cached_news 
            if news.published_at > cutoff_time
        ]
        
        # Analyser le sentiment et la pertinence
        for news in recent_news:
            news.sentiment_score = self.analyze_sentiment(news)
            news.relevance_score = self.calculate_relevance(news)
            
            # Déterminer le niveau d'impact
            if abs(news.sentiment_score) > 0.7 and news.relevance_score > 0.8:
                news.impact_level = "critical"
            elif abs(news.sentiment_score) > 0.5 and news.relevance_score > 0.6:
                news.impact_level = "high"
            elif abs(news.sentiment_score) > 0.3 and news.relevance_score > 0.4:
                news.impact_level = "medium"
            else:
                news.impact_level = "low"
        
        return sorted(recent_news, key=lambda x: x.relevance_score, reverse=True)

# Instance singleton
news_service = NewsService()
