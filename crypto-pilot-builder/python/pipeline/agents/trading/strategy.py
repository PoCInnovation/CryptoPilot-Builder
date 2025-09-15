"""Agent Strategy - Gestion des risques et génération de signaux de trading."""

import asyncio
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

from ..models.prediction import Prediction
from ..models.signal import Signal, SignalType
from ..models.trade import TradeRequest

logger = structlog.get_logger(__name__)

class StrategyAgent(Agent):
    """Agent Strategy pour la gestion des risques et décisions de trading."""
    
    def __init__(self):
        super().__init__(
            name="StrategyAgent",
            port=9003,
            seed="strategy_seed_12345",
            endpoint=["http://127.0.0.1:9003/submit"]
        )
        
        # Configuration de la stratégie
        self.risk_config = {
            "max_position_size": 0.1,  # 10% du capital
            "max_daily_loss": 0.05,    # 5% de perte max par jour
            "min_confidence": 0.7,     # Confiance minimale pour trader
            "stop_loss": 0.02,         # Stop loss à 2%
            "take_profit": 0.04,       # Take profit à 4%
            "max_open_trades": 3       # Nombre max de trades ouverts
        }
        
        # État du trading
        self.open_trades: Dict[str, Dict[str, Any]] = {}
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.last_reset = datetime.utcnow().date()
        
        # Historique des signaux
        self.signal_history: List[Signal] = []
        self.max_history = 100
        
        # Configuration des handlers
        self.on_message(model=Prediction)(self.handle_prediction)
        self.on_message(model=TradeRequest)(self.handle_trade_result)
        
        logger.info("StrategyAgent initialisé", 
                   risk_config=self.risk_config)
    
    async def handle_prediction(self, ctx: Context, sender: str, msg: Prediction):
        """Traite les prédictions et génère des signaux de trading."""
        try:
            logger.info("🔮 Prédiction reçue du Predictor", 
                       symbol=msg.symbol,
                       direction_prob=msg.direction_prob,
                       confidence=msg.confidence)
            
            # Vérification des conditions de trading
            if not self._check_trading_conditions(msg):
                logger.info("Conditions de trading non remplies", 
                           symbol=msg.symbol,
                           confidence=msg.confidence)
                return
            
            # Génération du signal
            signal = await self._generate_signal(msg)
            
            if signal and signal.signal_type != SignalType.HOLD:
                # Envoi au Trader
                await self._send_to_trader(ctx, signal)
                
                logger.info("📈 Signal généré", 
                           symbol=signal.symbol,
                           signal_type=signal.signal_type.value,
                           confidence=signal.confidence)
            
        except Exception as e:
            logger.error("❌ Erreur traitement prédiction", 
                        symbol=msg.symbol,
                        error=str(e))
    
    def _check_trading_conditions(self, prediction: Prediction) -> bool:
        """Vérifie si les conditions de trading sont remplies."""
        try:
            # Reset quotidien
            current_date = datetime.utcnow().date()
            if current_date > self.last_reset:
                self.daily_pnl = 0.0
                self.daily_trades = 0
                self.last_reset = current_date
                logger.info("Reset quotidien effectué")
            
            # Vérification de la confiance minimale
            if prediction.confidence < self.risk_config["min_confidence"]:
                logger.info("Confiance insuffisante", 
                           confidence=prediction.confidence,
                           min_required=self.risk_config["min_confidence"])
                return False
            
            # Vérification de la perte quotidienne
            if self.daily_pnl < -self.risk_config["max_daily_loss"]:
                logger.warning("Perte quotidienne maximale atteinte", 
                              daily_pnl=self.daily_pnl,
                              max_loss=self.risk_config["max_daily_loss"])
                return False
            
            # Vérification du nombre de trades ouverts
            if len(self.open_trades) >= self.risk_config["max_open_trades"]:
                logger.info("Nombre maximum de trades ouverts atteint", 
                           open_trades=len(self.open_trades),
                           max_trades=self.risk_config["max_open_trades"])
                return False
            
            # Vérification si on a déjà un trade ouvert sur ce symbole
            if prediction.symbol in self.open_trades:
                logger.info("Trade déjà ouvert sur ce symbole", 
                           symbol=prediction.symbol)
                return False
            
            return True
            
        except Exception as e:
            logger.error("Erreur vérification conditions trading", error=str(e))
            return False
    
    async def _generate_signal(self, prediction: Prediction) -> Optional[Signal]:
        """Génère un signal de trading basé sur la prédiction."""
        try:
            # Calcul du signal basé sur la probabilité de direction
            direction_prob = prediction.direction_prob
            
            # Seuils pour les signaux
            buy_threshold = 0.65
            sell_threshold = 0.35
            
            signal_type = SignalType.HOLD
            
            if direction_prob > buy_threshold:
                signal_type = SignalType.BUY
            elif direction_prob < sell_threshold:
                signal_type = SignalType.SELL
            
            # Calcul de la taille de position basée sur la confiance
            position_size = self._calculate_position_size(prediction)
            
            # Calcul du stop loss et take profit
            current_price = prediction.features_used.get("current_price", 1.0)
            stop_loss = current_price * (1 - self.risk_config["stop_loss"]) if signal_type == SignalType.BUY else current_price * (1 + self.risk_config["stop_loss"])
            take_profit = current_price * (1 + self.risk_config["take_profit"]) if signal_type == SignalType.BUY else current_price * (1 - self.risk_config["take_profit"])
            
            signal = Signal(
                symbol=prediction.symbol,
                signal_type=signal_type,
                confidence=prediction.confidence,
                price=current_price,
                position_size=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                prediction_data=prediction.dict(),
                timestamp=datetime.utcnow()
            )
            
            # Ajout à l'historique
            self.signal_history.append(signal)
            if len(self.signal_history) > self.max_history:
                self.signal_history = self.signal_history[-self.max_history:]
            
            return signal
            
        except Exception as e:
            logger.error("Erreur génération signal", 
                        symbol=prediction.symbol,
                        error=str(e))
            return None
    
    def _calculate_position_size(self, prediction: Prediction) -> float:
        """Calcule la taille de position basée sur la confiance et le risque."""
        try:
            # Taille de base
            base_size = self.risk_config["max_position_size"]
            
            # Ajustement basé sur la confiance
            confidence_factor = prediction.confidence
            
            # Ajustement basé sur la volatilité (plus de volatilité = position plus petite)
            volatility = prediction.volatility
            volatility_factor = max(0.3, 1.0 - volatility * 10)
            
            # Calcul de la taille finale
            position_size = base_size * confidence_factor * volatility_factor
            
            # Limitation à la taille maximale
            position_size = min(position_size, self.risk_config["max_position_size"])
            
            return round(position_size, 4)
            
        except Exception as e:
            logger.error("Erreur calcul taille position", error=str(e))
            return 0.01  # Taille minimale par défaut
    
    async def _send_to_trader(self, ctx: Context, signal: Signal):
        """Envoie le signal au Trader."""
        try:
            # Adresse du Trader (à configurer)
            trader_address = "agent1q2kxac3lxe4f9m9h2p9jwzqrv2y6s8ll0ctus7"
            
            await ctx.send(trader_address, signal)
            logger.info("Signal envoyé au Trader", 
                       symbol=signal.symbol,
                       signal_type=signal.signal_type.value)
            
        except Exception as e:
            logger.error("Erreur envoi au Trader", error=str(e))
    
    async def handle_trade_result(self, ctx: Context, sender: str, msg: TradeRequest):
        """Traite les résultats de trading pour mettre à jour l'état."""
        try:
            logger.info("📊 Résultat de trade reçu", 
                       symbol=msg.symbol,
                       status=msg.status,
                       pnl=msg.realized_pnl)
            
            # Mise à jour des statistiques
            if msg.realized_pnl:
                self.daily_pnl += msg.realized_pnl
                self.daily_trades += 1
            
            # Suppression du trade ouvert
            if msg.symbol in self.open_trades:
                del self.open_trades[msg.symbol]
            
            logger.info("État mis à jour", 
                       daily_pnl=self.daily_pnl,
                       daily_trades=self.daily_trades,
                       open_trades=len(self.open_trades))
            
        except Exception as e:
            logger.error("Erreur traitement résultat trade", error=str(e))
    
    async def run(self):
        """Démarre l'agent Strategy."""
        logger.info("🚀 Démarrage du StrategyAgent...")
        
        # Financement de l'agent si nécessaire
        await fund_agent_if_low(self.wallet.address())
        
        # Démarrage de l'agent
        await super().run()

if __name__ == "__main__":
    agent = StrategyAgent()
    asyncio.run(agent.run())
