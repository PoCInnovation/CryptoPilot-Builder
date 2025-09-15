"""Agent NewsCollector - Collecte et analyse des news crypto."""

import asyncio
import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

from ..models.news_data import NewsData, NewsItem, NewsRecommendation
from ...utils.circuit_breaker import CircuitBreaker

# Import des services existants
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../services'))
from services.news_service import news_service
from services.ai_analyzer import ai_analyzer

logger = structlog.get_logger(__name__)

class NewsCollectorAgent(Agent):
    """Agent de collecte et analyse des news crypto."""
    
    def __init__(self):
        logger.info("DEBUG: Début __init__ NewsCollectorAgent")
        super().__init__(
            name="news_collector",
            seed="news_collector_seed_123",
            port=9006,
            endpoint=["http://127.0.0.1:9006/submit"]
        )
        logger.info("DEBUG: Super().__init__ terminé")
        
        # Circuit breaker pour la robustesse
        self.circuit_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)
        logger.info("DEBUG: Circuit breaker créé")
        
        # Configuration de la collecte
        self.collection_interval = 300  # 5 minutes
        self.news_retention_hours = 24
        self.min_confidence_threshold = 0.3
        
        # Cryptos à surveiller
        self.crypto_symbols = ["BTC", "ETH", "ADA", "DOT", "SOL", "MATIC", "AVAX"]
        
        # Cache des news par symbole
        self.news_cache: Dict[str, List[NewsItem]] = {}
        self.last_collection = {}
        
        # Configuration de la tâche périodique
        logger.info("DEBUG: Configuration de la tâche périodique...")
        self.periodic_task = self.on_interval(period=self.collection_interval)(self.collect_news_data)
        logger.info("DEBUG: Tâche périodique configurée")
        
        logger.info("DEBUG: __init__ NewsCollectorAgent terminé", 
                   symbols=self.crypto_symbols)
    
    async def collect_news_data(self, ctx: Context):
        """Collecte périodique des news et génère des recommandations."""
        logger.info("DEBUG: Début collect_news_data")
        try:
            # Récupérer les news récentes
            recent_news = await self._fetch_recent_news()
            
            if not recent_news:
                logger.warning("Aucune news récupérée")
                return
            
            # Grouper les news par symbole crypto
            news_by_symbol = self._group_news_by_symbol(recent_news)
            
            # Traiter chaque symbole
            for symbol, news_items in news_by_symbol.items():
                if news_items:
                    await self._process_news_for_symbol(ctx, symbol, news_items)
                    
        except Exception as e:
            logger.error("DEBUG: Erreur lors de la collecte de news", error=str(e))
            logger.error("DEBUG: Stack trace collect_news_data", exc_info=True)
    
    async def _fetch_recent_news(self) -> List[NewsItem]:
        """Récupère les news récentes via le NewsService."""
        try:
            # Utilisation du circuit breaker
            @self.circuit_breaker
            def fetch_news():
                return news_service.get_recent_news(hours=1)
            
            logger.info("DEBUG: Récupération des news...")
            news_items = fetch_news()
            logger.info(f"DEBUG: {len(news_items)} news récupérées")
            
            # Convertir en NewsItem
            converted_news = []
            for news in news_items:
                news_item = NewsItem(
                    id=news.id,
                    title=news.title,
                    content=news.content,
                    source=news.source,
                    published_at=news.published_at,
                    url=news.url,
                    sentiment_score=news.sentiment_score,
                    relevance_score=news.relevance_score,
                    crypto_mentions=news.crypto_mentions or [],
                    impact_level=news.impact_level
                )
                converted_news.append(news_item)
            
            return converted_news
            
        except Exception as e:
            logger.error("Erreur récupération news", error=str(e))
            return []
    
    def _group_news_by_symbol(self, news_items: List[NewsItem]) -> Dict[str, List[NewsItem]]:
        """Groupe les news par symbole crypto."""
        grouped = {}
        
        for news in news_items:
            if news.crypto_mentions:
                for symbol in news.crypto_mentions:
                    if symbol in self.crypto_symbols:
                        if symbol not in grouped:
                            grouped[symbol] = []
                        grouped[symbol].append(news)
        
        return grouped
    
    async def _process_news_for_symbol(self, ctx: Context, symbol: str, news_items: List[NewsItem]):
        """Traite les news pour un symbole et génère des recommandations."""
        try:
            logger.info(f"DEBUG: Traitement des news pour {symbol}", count=len(news_items))
            
            # Générer des recommandations via l'AI Analyzer
            recommendations = await self._generate_recommendations(symbol, news_items)
            
            # Calculer les métriques agrégées
            aggregated_sentiment = self._calculate_aggregated_sentiment(news_items)
            aggregated_confidence = self._calculate_aggregated_confidence(recommendations)
            dominant_action = self._determine_dominant_action(recommendations)
            
            # Compter les news à fort impact
            high_impact_count = sum(1 for news in news_items if news.impact_level in ["high", "critical"])
            
            # Créer l'objet NewsData
            news_data = NewsData(
                symbol=symbol,
                news_items=news_items,
                recommendations=recommendations,
                aggregated_sentiment=aggregated_sentiment,
                aggregated_confidence=aggregated_confidence,
                dominant_action=dominant_action,
                news_count=len(news_items),
                high_impact_news_count=high_impact_count,
                timestamp=datetime.utcnow()
            )
            
            # Envoyer au DataAggregator
            await self._send_to_aggregator(ctx, news_data)
            
            # Mettre à jour le cache
            self.news_cache[symbol] = news_items
            self.last_collection[symbol] = datetime.utcnow()
            
            logger.info(f"News traitées pour {symbol}", 
                       sentiment=aggregated_sentiment,
                       confidence=aggregated_confidence,
                       action=dominant_action)
            
        except Exception as e:
            logger.error(f"Erreur traitement news pour {symbol}", error=str(e))
    
    async def _generate_recommendations(self, symbol: str, news_items: List[NewsItem]) -> List[NewsRecommendation]:
        """Génère des recommandations basées sur les news."""
        try:
            recommendations = []
            
            # Utiliser l'AI Analyzer existant
            market_context = ai_analyzer.get_market_context()
            alerts = ai_analyzer.analyze_news_for_investment(news_items, market_context)
            
            # Convertir les alertes en recommandations
            for alert in alerts:
                if alert.crypto_symbol == symbol and alert.confidence_score >= self.min_confidence_threshold:
                    recommendation = NewsRecommendation(
                        action=alert.alert_type.lower(),
                        confidence=alert.confidence_score,
                        reasoning=alert.reasoning,
                        risk_level=self._assess_risk_level(alert.confidence_score),
                        time_horizon=self._determine_time_horizon(alert.reasoning),
                        news_id=alert.news_id,
                        timestamp=datetime.utcnow()
                    )
                    recommendations.append(recommendation)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Erreur génération recommandations pour {symbol}", error=str(e))
            return []
    
    def _calculate_aggregated_sentiment(self, news_items: List[NewsItem]) -> float:
        """Calcule le sentiment agrégé des news."""
        if not news_items:
            return 0.0
        
        # Moyenne pondérée par la pertinence
        total_weight = 0.0
        weighted_sentiment = 0.0
        
        for news in news_items:
            weight = news.relevance_score
            weighted_sentiment += news.sentiment_score * weight
            total_weight += weight
        
        return weighted_sentiment / total_weight if total_weight > 0 else 0.0
    
    def _calculate_aggregated_confidence(self, recommendations: List[NewsRecommendation]) -> float:
        """Calcule la confiance agrégée des recommandations."""
        if not recommendations:
            return 0.0
        
        # Moyenne des confidences
        total_confidence = sum(rec.confidence for rec in recommendations)
        return total_confidence / len(recommendations)
    
    def _determine_dominant_action(self, recommendations: List[NewsRecommendation]) -> str:
        """Détermine l'action dominante basée sur les recommandations."""
        if not recommendations:
            return "hold"
        
        # Compter les actions pondérées par la confiance
        action_scores = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
        
        for rec in recommendations:
            action_scores[rec.action] += rec.confidence
        
        # Retourner l'action avec le score le plus élevé
        return max(action_scores, key=action_scores.get)
    
    def _assess_risk_level(self, confidence: float) -> str:
        """Évalue le niveau de risque basé sur la confiance."""
        if confidence >= 0.8:
            return "low"
        elif confidence >= 0.6:
            return "medium"
        else:
            return "high"
    
    def _determine_time_horizon(self, reasoning: str) -> str:
        """Détermine l'horizon temporel basé sur le raisonnement."""
        reasoning_lower = reasoning.lower()
        
        if any(keyword in reasoning_lower for keyword in ['adoption', 'partnership', 'regulation', 'long-term']):
            return "long_term"
        elif any(keyword in reasoning_lower for keyword in ['upgrade', 'launch', 'release', 'integration']):
            return "medium_term"
        else:
            return "short_term"
    
    async def _send_to_aggregator(self, ctx: Context, news_data: NewsData):
        """Envoie les données de news au DataAggregator."""
        try:
            # Adresse du DataAggregator (à configurer)
            aggregator_address = "agent1q2kxac3lxe4f9m9h2p9jwzqrv2y6s8ll0ctus7"
            
            await ctx.send(aggregator_address, news_data)
            logger.info("Données de news envoyées au DataAggregator", 
                       symbol=news_data.symbol,
                       news_count=news_data.news_count)
            
        except Exception as e:
            logger.error("Erreur envoi au DataAggregator", error=str(e))
    
    async def cleanup(self):
        """Nettoyage des ressources."""
        logger.info("DEBUG: Nettoyage NewsCollector terminé")

if __name__ == "__main__":
    agent = NewsCollectorAgent()
    agent.run()
