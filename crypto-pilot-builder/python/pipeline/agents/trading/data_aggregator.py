"""Agent DataAggregator - Fusionne les données de marché et de news."""

import asyncio
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

from ..models.market_data import MarketData, NewsRecommendation
from ..models.news_data import NewsData

logger = structlog.get_logger(__name__)

class DataAggregatorAgent(Agent):
    """Agent qui fusionne les données de marché et de news avant le Predictor."""
    
    def __init__(self):
        logger.info("DEBUG: Début __init__ DataAggregatorAgent")
        super().__init__(
            name="data_aggregator",
            seed="data_aggregator_seed_123",
            port=9007,
            endpoint=["http://127.0.0.1:9007/submit"]
        )
        logger.info("DEBUG: Super().__init__ terminé")
        
        # Cache des données en attente de fusion
        self.pending_market_data: Dict[str, MarketData] = {}
        self.pending_news_data: Dict[str, NewsData] = {}
        
        # Configuration de la fusion
        self.fusion_timeout = 30  # secondes
        self.max_wait_time = 60  # secondes maximum d'attente
        
        # Configuration des handlers
        self.on_message(model=MarketData)(self.handle_market_data)
        self.on_message(model=NewsData)(self.handle_news_data)
        
        # Tâche de nettoyage périodique
        self.cleanup_task = self.on_interval(period=300)(self.cleanup_expired_data)
        
        logger.info("DEBUG: __init__ DataAggregatorAgent terminé")
    
    async def handle_market_data(self, ctx: Context, sender: str, msg: MarketData):
        """Traite les données de marché reçues du DataCollector."""
        try:
            logger.info("📊 Données de marché reçues", 
                       symbol=msg.symbol,
                       sender=sender)
            
            # Stocker les données de marché
            self.pending_market_data[msg.symbol] = msg
            
            # Vérifier si on a les données de news correspondantes
            if msg.symbol in self.pending_news_data:
                await self._fuse_and_send_data(ctx, msg.symbol)
            else:
                logger.info("En attente des données de news", symbol=msg.symbol)
                
        except Exception as e:
            logger.error("❌ Erreur traitement données marché", 
                        symbol=msg.symbol,
                        error=str(e))
    
    async def handle_news_data(self, ctx: Context, sender: str, msg: NewsData):
        """Traite les données de news reçues du NewsCollector."""
        try:
            logger.info("📰 Données de news reçues", 
                       symbol=msg.symbol,
                       sender=sender,
                       news_count=msg.news_count)
            
            # Stocker les données de news
            self.pending_news_data[msg.symbol] = msg
            
            # Vérifier si on a les données de marché correspondantes
            if msg.symbol in self.pending_market_data:
                await self._fuse_and_send_data(ctx, msg.symbol)
            else:
                logger.info("En attente des données de marché", symbol=msg.symbol)
                
        except Exception as e:
            logger.error("❌ Erreur traitement données news", 
                        symbol=msg.symbol,
                        error=str(e))
    
    async def _fuse_and_send_data(self, ctx: Context, symbol: str):
        """Fusionne les données de marché et de news et les envoie au Predictor."""
        try:
            market_data = self.pending_market_data.get(symbol)
            news_data = self.pending_news_data.get(symbol)
            
            if not market_data or not news_data:
                logger.warning("Données manquantes pour la fusion", 
                              symbol=symbol,
                              has_market=market_data is not None,
                              has_news=news_data is not None)
                return
            
            # Fusionner les données
            fused_data = await self._fuse_market_and_news_data(market_data, news_data)
            
            # Envoyer au Predictor
            await self._send_to_predictor(ctx, fused_data)
            
            # Nettoyer les données fusionnées
            self._cleanup_fused_data(symbol)
            
            logger.info("✅ Données fusionnées et envoyées", 
                       symbol=symbol,
                       news_count=news_data.news_count,
                       recommendations_count=len(news_data.recommendations))
            
        except Exception as e:
            logger.error("❌ Erreur fusion données", 
                        symbol=symbol,
                        error=str(e))
    
    async def _fuse_market_and_news_data(self, market_data: MarketData, news_data: NewsData) -> MarketData:
        """Fusionne les données de marché et de news."""
        try:
            # Convertir les recommandations de news au format MarketData
            news_recommendations = []
            for rec in news_data.recommendations:
                news_rec = NewsRecommendation(
                    action=rec.action,
                    confidence=rec.confidence,
                    reasoning=rec.reasoning,
                    source="news_analysis",
                    news_id=rec.news_id,
                    timestamp=rec.timestamp
                )
                news_recommendations.append(news_rec)
            
            # Créer les données fusionnées
            fused_data = MarketData(
                symbol=market_data.symbol,
                timeframe=market_data.timeframe,
                ohlcv=market_data.ohlcv,
                features=market_data.features,
                news_sentiment=market_data.news_sentiment,
                social_sentiment=market_data.social_sentiment,
                # Nouvelles données de news
                news_recommendations=news_recommendations,
                news_sentiment_aggregated=news_data.aggregated_sentiment,
                news_confidence_aggregated=news_data.aggregated_confidence,
                news_count=news_data.news_count,
                timestamp=datetime.utcnow()
            )
            
            # Mettre à jour le sentiment des news si disponible
            if news_data.aggregated_sentiment is not None:
                fused_data.news_sentiment = news_data.aggregated_sentiment
            
            return fused_data
            
        except Exception as e:
            logger.error("Erreur fusion données", error=str(e))
            return market_data  # Retourner les données de marché seules en cas d'erreur
    
    async def _send_to_predictor(self, ctx: Context, fused_data: MarketData):
        """Envoie les données fusionnées au Predictor."""
        try:
            # Adresse du Predictor (à configurer)
            predictor_address = "agent1q2kxac3lxe4f9m9h2p9jwzqrv2y6s8ll0ctus7"
            
            await ctx.send(predictor_address, fused_data)
            logger.info("Données fusionnées envoyées au Predictor", 
                       symbol=fused_data.symbol,
                       news_count=fused_data.news_count,
                       recommendations_count=len(fused_data.news_recommendations) if fused_data.news_recommendations else 0)
            
        except Exception as e:
            logger.error("Erreur envoi au Predictor", error=str(e))
    
    def _cleanup_fused_data(self, symbol: str):
        """Nettoie les données fusionnées du cache."""
        if symbol in self.pending_market_data:
            del self.pending_market_data[symbol]
        if symbol in self.pending_news_data:
            del self.pending_news_data[symbol]
    
    async def cleanup_expired_data(self, ctx: Context):
        """Nettoie les données expirées du cache."""
        try:
            current_time = datetime.utcnow()
            expired_symbols = []
            
            # Vérifier les données de marché expirées
            for symbol, data in self.pending_market_data.items():
                if (current_time - data.timestamp).total_seconds() > self.max_wait_time:
                    expired_symbols.append(symbol)
            
            # Vérifier les données de news expirées
            for symbol, data in self.pending_news_data.items():
                if (current_time - data.timestamp).total_seconds() > self.max_wait_time:
                    if symbol not in expired_symbols:
                        expired_symbols.append(symbol)
            
            # Nettoyer les données expirées
            for symbol in expired_symbols:
                self._cleanup_fused_data(symbol)
                logger.warning("Données expirées nettoyées", symbol=symbol)
            
            if expired_symbols:
                logger.info("Nettoyage terminé", 
                           expired_count=len(expired_symbols),
                           remaining_market=len(self.pending_market_data),
                           remaining_news=len(self.pending_news_data))
                
        except Exception as e:
            logger.error("Erreur nettoyage données expirées", error=str(e))
    
    def get_aggregation_status(self) -> Dict[str, Any]:
        """Retourne le statut de l'agrégation."""
        return {
            "pending_market_data": len(self.pending_market_data),
            "pending_news_data": len(self.pending_news_data),
            "market_symbols": list(self.pending_market_data.keys()),
            "news_symbols": list(self.pending_news_data.keys()),
            "fusion_timeout": self.fusion_timeout,
            "max_wait_time": self.max_wait_time
        }
    
    async def run(self):
        """Démarre l'agent DataAggregator."""
        logger.info("🚀 Démarrage du DataAggregatorAgent...")
        
        # Financement de l'agent si nécessaire
        await fund_agent_if_low(self.wallet.address())
        
        # Démarrage de l'agent
        await super().run()

if __name__ == "__main__":
    agent = DataAggregatorAgent()
    asyncio.run(agent.run())
