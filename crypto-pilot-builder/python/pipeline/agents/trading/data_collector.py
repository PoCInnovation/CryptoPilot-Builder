"""Agent DataCollector - Collecte des données Ethereum/MetaMask."""

import asyncio
import aiohttp
from typing import List, Dict, Any
from datetime import datetime, timedelta
import structlog
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

from ..models.market_data import MarketData, OHLCV
from ...utils.circuit_breaker import CircuitBreaker

logger = structlog.get_logger(__name__)

class DataCollectorAgent(Agent):
    """Agent de collecte de données Ethereum/MetaMask."""
    
    def __init__(self):
        logger.info("DEBUG: Début __init__ DataCollectorAgent")
        super().__init__(
            name="data_collector",
            seed="data_collector_seed_123",
            port=9001,
            endpoint=["http://127.0.0.1:9001/submit"]
        )
        logger.info("DEBUG: Super().__init__ terminé")
        
        # Circuit breaker pour la robustesse
        self.circuit_breaker = CircuitBreaker(fail_max=5, reset_timeout=60)
        logger.info("DEBUG: Circuit breaker créé")
        
        # Cryptos populaires via CoinGecko
        self.cryptos = {
            "bitcoin": "BTC",
            "ethereum": "ETH"
        }
        
        # Plus besoin de client Ethereum pour le trading simple
        logger.info("DEBUG: DataCollector configuré pour prix uniquement")
        
        # Configuration de la tâche périodique
        logger.info("DEBUG: Configuration de la tâche périodique...")
        self.periodic_task = self.on_interval(period=60)(self.collect_market_data)
        logger.info("DEBUG: Tâche périodique configurée")
        
        self.collection_interval = 60  # secondes
        logger.info("DEBUG: __init__ DataCollectorAgent terminé", cryptos=list(self.cryptos.keys()))
    
    async def collect_market_data(self, ctx: Context):
        """Collecte périodique des données de marché."""
        logger.info("DEBUG: Début collect_market_data")
        try:
            for crypto_id, symbol in self.cryptos.items():
                logger.info("DEBUG: Collecte pour crypto", crypto=crypto_id)
                await self._collect_crypto_data(ctx, crypto_id, symbol)
                    
        except Exception as e:
            logger.error("DEBUG: Erreur lors de la collecte de données", error=str(e))
            logger.error("DEBUG: Stack trace collect_market_data", exc_info=True)
    
    async def _collect_crypto_data(self, ctx: Context, crypto_id: str, symbol: str):
        """Collecte les données pour une crypto via CoinGecko."""
        logger.info("DEBUG: Début _collect_crypto_data", crypto=crypto_id)
        try:
            # Utilisation du circuit breaker
            @self.circuit_breaker
            async def fetch_data():
                logger.info("DEBUG: Début fetch_data")
                # Récupération du prix en temps réel via CoinGecko
                from ...utils.market_data_service import market_data_service
                market_data = await market_data_service.get_crypto_price(crypto_id)
                logger.info("DEBUG: Prix CoinGecko récupéré", price=market_data)
                
                return {
                    "price": market_data,
                    "symbol": symbol
                }
            
            logger.info("DEBUG: Appel fetch_data...")
            data = await fetch_data()
            logger.info("DEBUG: fetch_data terminé", data=data)
            
            if not data["price"]:
                logger.warning("Aucun prix reçu", crypto=crypto_id)
                return
            
            # Création d'un OHLCV simple
            ohlcv = OHLCV(
                timestamp=int(datetime.now().timestamp() * 1000),
                open=data["price"],
                high=data["price"] * 1.001,  # +0.1%
                low=data["price"] * 0.999,   # -0.1%
                close=data["price"],
                volume=1000000  # Volume simulé
            )
            
            # Calcul des features techniques basiques
            features = self._calculate_features([ohlcv])
            
            # Création de l'objet MarketData
            market_data = MarketData(
                symbol=f"{symbol}/USD",
                timeframe="1m",
                ohlcv=[ohlcv],
                features=features,
                timestamp=datetime.utcnow()
            )
            
            # Envoi au Predictor
            await self._send_to_predictor(ctx, market_data)
            
            logger.info("Données collectées avec succès", 
                       crypto=crypto_id, 
                       price=data["price"])
            
        except Exception as e:
            logger.error("Erreur collecte crypto", 
                        crypto=crypto_id, 
                        error=str(e))
    
    def _calculate_features(self, ohlcv_list: List[OHLCV]) -> Dict[str, Any]:
        """Calcule les features techniques basiques."""
        if len(ohlcv_list) < 1:
            return {}
        
        closes = [c.close for c in ohlcv_list]
        volumes = [c.volume for c in ohlcv_list]
        
        # Features simples pour l'exemple
        return {
            "current_price": closes[-1],
            "price_change_1m": (closes[-1] - closes[0]) / closes[0] if len(closes) > 1 else 0,
            "volume_1m": sum(volumes),
            "volatility": abs(closes[-1] - closes[0]) / closes[0] if len(closes) > 1 else 0
        }
    
    async def _send_to_predictor(self, ctx: Context, market_data: MarketData):
        """Envoie les données au Predictor."""
        try:
            # Adresse du Predictor (à configurer)
            predictor_address = "agent1q2kxac3lxe4f9m9h2p9jwzqrv2y6s8ll0ctus7"
            
            await ctx.send(predictor_address, market_data)
            logger.info("Données envoyées au Predictor", 
                       symbol=market_data.symbol,
                       timeframe=market_data.timeframe)
            
        except Exception as e:
            logger.error("Erreur envoi au Predictor", error=str(e))
    
    async def cleanup(self):
        """Nettoyage des ressources."""
        logger.info("DEBUG: Nettoyage DataCollector terminé")

if __name__ == "__main__":
    agent = DataCollectorAgent()
    agent.run()
