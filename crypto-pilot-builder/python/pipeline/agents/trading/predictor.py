"""Agent Predictor - Modèle d'IA pour l'analyse de séries temporelles."""

import asyncio
import numpy as np
import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

from ..models.market_data import MarketData
from ..models.prediction import Prediction
from ..models.signal import Signal
from ...utils.asi_model import ASIOneModel
from ...utils.technical_indicators import TechnicalIndicators

logger = structlog.get_logger(__name__)

class PredictorAgent(Agent):
    """Agent Predictor avec modèles ML pour l'analyse de séries temporelles."""
    
    def __init__(self):
        super().__init__(
            name="PredictorAgent",
            port=9002,
            seed="predictor_seed_12345",
            endpoint=["http://127.0.0.1:9002/submit"]
        )
        
        # Configuration du modèle
        self.model_name = "ASI:One-Mini"
        self.prediction_horizon = 5  # minutes
        self.confidence_threshold = 0.6
        
        # Cache pour les données historiques
        self.price_history: Dict[str, List[float]] = {}
        self.volume_history: Dict[str, List[float]] = {}
        self.max_history_length = 100
        
        # Modèle ASI:One
        self.asi_model = ASIOneModel(model="asi1-mini")
        
        # Configuration des handlers
        self.on_message(model=MarketData)(self.handle_market_data)
        
        logger.info("PredictorAgent initialisé", 
                   model=self.model_name,
                   horizon=self.prediction_horizon,
                   asi_model=self.asi_model.model)
    
    async def _test_asi_connection(self) -> bool:
        """Teste la connexion au modèle ASI:One."""
        try:
            return await self.asi_model.test_connection()
        except Exception as e:
            logger.error("Erreur test connexion ASI:One", error=str(e))
            return False
    
    async def handle_market_data(self, ctx: Context, sender: str, msg: MarketData):
        """Traite les données de marché et génère des prédictions."""
        try:
            logger.info("📊 Données reçues du DataCollector", 
                       symbol=msg.symbol,
                       timeframe=msg.timeframe,
                       ohlcv_count=len(msg.ohlcv))
            
            # Extraction des prix de clôture
            prices = [candle.close for candle in msg.ohlcv]
            symbol = msg.symbol
            
            # Mise à jour de l'historique
            if symbol not in self.price_history:
                self.price_history[symbol] = []
            
            self.price_history[symbol].extend(prices)
            
            # Garder seulement les dernières données
            if len(self.price_history[symbol]) > self.max_history_length:
                self.price_history[symbol] = self.price_history[symbol][-self.max_history_length:]
            
            # Génération de la prédiction
            prediction = await self._generate_prediction(symbol, prices, msg.features)
            
            if prediction:
                # Envoi au Strategy
                await self._send_to_strategy(ctx, prediction)
                
                logger.info("🔮 Prédiction générée", 
                           symbol=prediction.symbol,
                           direction_prob=prediction.direction_prob,
                           confidence=prediction.confidence)
            
        except Exception as e:
            logger.error("❌ Erreur traitement données marché", 
                        symbol=msg.symbol,
                        error=str(e))
    
    async def _generate_prediction(self, symbol: str, prices: List[float], features: Dict[str, Any]) -> Optional[Prediction]:
        """Génère une prédiction basée sur les données historiques avec ASI:One."""
        try:
            if len(prices) < 20:
                logger.warning("Données insuffisantes pour prédiction ASI:One", 
                              symbol=symbol,
                              data_points=len(prices))
                return None
            
            # Calculer les indicateurs techniques
            technical_indicators = TechnicalIndicators.calculate_all_indicators(prices)
            
            # Récupérer l'historique des volumes si disponible
            volumes = self.volume_history.get(symbol, [1000000] * len(prices))  # Volume par défaut
            
            # Générer la prédiction avec ASI:One
            prediction_result = await self.asi_model.predict_price_direction(
                price_history=prices,
                volume_history=volumes,
                technical_indicators=technical_indicators,
                symbol=symbol
            )
            
            # Créer l'objet Prediction
            prediction = Prediction(
                symbol=symbol,
                horizon=self.prediction_horizon,
                direction_prob=prediction_result["direction_probability"],
                volatility=technical_indicators.get("volatility", 0.01),
                confidence=prediction_result["confidence"],
                model_name=prediction_result["model_name"],
                features_used=prediction_result["features_used"],
                timestamp=datetime.utcnow()
            )
            
            logger.info("🔮 Prédiction ASI:One générée", 
                       symbol=symbol,
                       direction_prob=prediction_result["direction_probability"],
                       confidence=prediction_result["confidence"],
                       model=prediction_result["model_name"])
            
            return prediction
            
        except Exception as e:
            logger.error("❌ Erreur génération prédiction ASI:One", 
                        symbol=symbol,
                        error=str(e))
            # Fallback vers simulation
            return await self._generate_simulation_prediction(symbol, prices, features)
    
    async def _generate_simulation_prediction(self, symbol: str, prices: List[float], features: Dict[str, Any]) -> Optional[Prediction]:
        """Génère une prédiction de simulation en cas d'échec ASI:One."""
        try:
            # Calculer les indicateurs techniques
            technical_indicators = TechnicalIndicators.calculate_all_indicators(prices)
            
            # Logique de simulation basée sur les indicateurs
            current_price = prices[-1]
            price_change = ((current_price - prices[-2]) / prices[-2]) if len(prices) > 1 else 0
            
            # Base de probabilité
            base_prob = 0.5
            
            # Influence du RSI
            rsi = technical_indicators.get("rsi", 50)
            if rsi < 30:  # Oversold
                base_prob += 0.2
            elif rsi > 70:  # Overbought
                base_prob -= 0.2
            
            # Influence de la tendance
            if price_change > 0.01:
                base_prob += 0.1
            elif price_change < -0.01:
                base_prob -= 0.1
            
            # Ajouter du bruit
            import random
            direction_prob = base_prob + random.uniform(-0.05, 0.05)
            direction_prob = max(0.0, min(1.0, direction_prob))
            
            confidence = random.uniform(0.6, 0.9)
            
            prediction = Prediction(
                symbol=symbol,
                horizon=self.prediction_horizon,
                direction_prob=direction_prob,
                volatility=technical_indicators.get("volatility", 0.01),
                confidence=confidence,
                model_name=f"{self.model_name}-SIMULATION",
                features_used={
                    "price_history_length": len(prices),
                    "technical_indicators": bool(technical_indicators),
                    "simulation_mode": True
                },
                timestamp=datetime.utcnow()
            )
            
            logger.info("🔮 Prédiction simulation générée (fallback)", 
                       symbol=symbol,
                       direction_prob=direction_prob,
                       confidence=confidence)
            
            return prediction
            
        except Exception as e:
            logger.error("❌ Erreur prédiction simulation", 
                        symbol=symbol,
                        error=str(e))
            return None
        
        # Facteurs qui influencent la prédiction
        price_momentum = features["price_change_1m"] + features["price_change_5m"] * 0.5
        volatility_factor = features["volatility"] * 100
        volume_factor = min(1.0, features["volume"] / 1000000)
        
        # Calcul de la probabilité de hausse
        base_prob = 0.5
        
        # Ajustement basé sur le momentum
        if price_momentum > 0.01:  # Tendance haussière
            base_prob += 0.2
        elif price_momentum < -0.01:  # Tendance baissière
            base_prob -= 0.2
        
        # Ajustement basé sur la volatilité
        if volatility_factor > 0.05:  # Volatilité élevée
            base_prob += 0.1
        
        # Ajustement basé sur le volume
        base_prob += (volume_factor - 0.5) * 0.1
        
        # Ajout de bruit aléatoire pour simuler l'incertitude
        noise = np.random.normal(0, 0.05)
        final_prob = base_prob + noise
        
        # Normalisation entre 0 et 1
        return max(0.0, min(1.0, final_prob))
    
    async def _send_to_strategy(self, ctx: Context, prediction: Prediction):
        """Envoie la prédiction au Strategy."""
        try:
            # Adresse du Strategy (à configurer)
            strategy_address = "agent1q2kxac3lxe4f9m9h2p9jwzqrv2y6s8ll0ctus7"
            
            await ctx.send(strategy_address, prediction)
            logger.info("Prédiction envoyée au Strategy", 
                       symbol=prediction.symbol,
                       confidence=prediction.confidence)
            
        except Exception as e:
            logger.error("Erreur envoi au Strategy", error=str(e))
    
    async def run(self):
        """Démarre l'agent Predictor."""
        logger.info("🚀 Démarrage du PredictorAgent...")
        
        # Financement de l'agent si nécessaire
        await fund_agent_if_low(self.wallet.address())
        
        # Démarrage de l'agent
        await super().run()

if __name__ == "__main__":
    agent = PredictorAgent()
    asyncio.run(agent.run())
