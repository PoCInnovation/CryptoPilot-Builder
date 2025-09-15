"""Agent Trader - Exécution des ordres de trading (CEX/DEX)."""

import asyncio
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

from ..models.signal import Signal, SignalType
from ..models.trade import TradeRequest, TradeStatus, TradeType
from ..models.prediction import Prediction

logger = structlog.get_logger(__name__)

class TraderAgent(Agent):
    """Agent Trader pour l'exécution des ordres de trading."""
    
    def __init__(self):
        super().__init__(
            name="TraderAgent",
            port=9004,
            seed="trader_seed_12345",
            endpoint=["http://127.0.0.1:9004/submit"]
        )
        
        # Configuration du trading
        self.trading_config = {
            "paper_trading": True,  # Mode simulation par défaut
            "max_slippage": 0.005,  # 0.5% de slippage max
            "min_order_size": 10,   # Taille minimale en USD
            "max_order_size": 1000, # Taille maximale en USD
            "retry_attempts": 3,    # Nombre de tentatives
            "retry_delay": 1        # Délai entre tentatives en secondes
        }
        
        # État des trades
        self.open_trades: Dict[str, Dict[str, Any]] = {}
        self.trade_history: List[Dict[str, Any]] = []
        self.total_pnl = 0.0
        self.total_trades = 0
        self.successful_trades = 0
        
        # Simulation de capital
        self.capital = 10000.0  # 10k USD de capital initial
        self.available_capital = self.capital
        
        # Configuration des handlers
        self.on_message(model=Signal)(self.handle_signal)
        self.on_message(model=Prediction)(self.handle_price_update)
        
        logger.info("TraderAgent initialisé", 
                   trading_config=self.trading_config,
                   capital=self.capital)
    
    async def handle_signal(self, ctx: Context, sender: str, msg: Signal):
        """Traite les signaux de trading et exécute les ordres."""
        try:
            logger.info("📈 Signal reçu du Strategy", 
                       symbol=msg.symbol,
                       signal_type=msg.signal_type.value,
                       confidence=msg.confidence,
                       price=msg.price)
            
            # Vérification des conditions d'exécution
            if not self._check_execution_conditions(msg):
                logger.info("Conditions d'exécution non remplies", 
                           symbol=msg.symbol)
                return
            
            # Exécution du trade
            trade_result = await self._execute_trade(msg)
            
            if trade_result:
                # Envoi du résultat au Logger
                await self._send_to_logger(ctx, trade_result)
                
                logger.info("✅ Trade exécuté", 
                           symbol=trade_result.symbol,
                           status=trade_result.status.value,
                           pnl=trade_result.realized_pnl)
            
        except Exception as e:
            logger.error("❌ Erreur exécution trade", 
                        symbol=msg.symbol,
                        error=str(e))
    
    def _check_execution_conditions(self, signal: Signal) -> bool:
        """Vérifie si les conditions d'exécution sont remplies."""
        try:
            # Vérification du capital disponible
            required_capital = signal.price * signal.position_size * self.capital
            if required_capital > self.available_capital:
                logger.warning("Capital insuffisant", 
                              required=required_capital,
                              available=self.available_capital)
                return False
            
            # Vérification de la taille minimale
            if required_capital < self.trading_config["min_order_size"]:
                logger.info("Ordre trop petit", 
                           size=required_capital,
                           min_size=self.trading_config["min_order_size"])
                return False
            
            # Vérification de la taille maximale
            if required_capital > self.trading_config["max_order_size"]:
                logger.warning("Ordre trop grand", 
                              size=required_capital,
                              max_size=self.trading_config["max_order_size"])
                return False
            
            # Vérification si on a déjà un trade ouvert sur ce symbole
            if signal.symbol in self.open_trades:
                logger.info("Trade déjà ouvert sur ce symbole", 
                           symbol=signal.symbol)
                return False
            
            return True
            
        except Exception as e:
            logger.error("Erreur vérification conditions exécution", error=str(e))
            return False
    
    async def _execute_trade(self, signal: Signal) -> Optional[TradeRequest]:
        """Exécute un trade basé sur le signal."""
        try:
            # Calcul de la taille de l'ordre
            order_size = signal.price * signal.position_size * self.capital
            
            # Simulation de l'exécution
            execution_price = await self._simulate_execution(signal)
            
            if not execution_price:
                logger.error("Échec de l'exécution", symbol=signal.symbol)
                return None
            
            # Calcul du slippage
            slippage = abs(execution_price - signal.price) / signal.price
            
            if slippage > self.trading_config["max_slippage"]:
                logger.warning("Slippage trop élevé", 
                              slippage=slippage,
                              max_slippage=self.trading_config["max_slippage"])
                return None
            
            # Création du trade
            trade_id = f"trade_{datetime.utcnow().timestamp()}_{signal.symbol}"
            
            trade = TradeRequest(
                trade_id=trade_id,
                symbol=signal.symbol,
                trade_type=TradeType.MARKET,
                side=signal.signal_type,
                quantity=signal.position_size,
                price=execution_price,
                stop_loss=signal.stop_loss,
                take_profit=signal.take_profit,
                status=TradeStatus.FILLED,
                timestamp=datetime.utcnow(),
                signal_data=signal.dict()
            )
            
            # Mise à jour du capital
            self.available_capital -= order_size
            
            # Ajout aux trades ouverts
            self.open_trades[signal.symbol] = {
                "trade_id": trade_id,
                "entry_price": execution_price,
                "quantity": signal.position_size,
                "stop_loss": signal.stop_loss,
                "take_profit": signal.take_profit,
                "timestamp": datetime.utcnow()
            }
            
            # Ajout à l'historique
            self.trade_history.append(trade.dict())
            self.total_trades += 1
            
            logger.info("Trade créé", 
                       trade_id=trade_id,
                       execution_price=execution_price,
                       slippage=slippage)
            
            return trade
            
        except Exception as e:
            logger.error("Erreur exécution trade", 
                        symbol=signal.symbol,
                        error=str(e))
            return None
    
    async def _simulate_execution(self, signal: Signal) -> Optional[float]:
        """Simule l'exécution d'un ordre (remplacé par vraie API en production)."""
        try:
            # Simulation de délai d'exécution
            await asyncio.sleep(0.1)
            
            # Simulation de prix d'exécution avec slippage aléatoire
            base_price = signal.price
            slippage_factor = 0.001  # 0.1% de slippage moyen
            
            # Slippage aléatoire
            slippage = (asyncio.get_event_loop().time() % 1000) / 10000 - 0.005  # ±0.5%
            
            execution_price = base_price * (1 + slippage)
            
            # Simulation de succès/échec (95% de succès)
            success_rate = 0.95
            if (asyncio.get_event_loop().time() % 100) / 100 > success_rate:
                logger.warning("Simulation d'échec d'exécution", symbol=signal.symbol)
                return None
            
            return round(execution_price, 6)
            
        except Exception as e:
            logger.error("Erreur simulation exécution", error=str(e))
            return None
    
    async def _send_to_logger(self, ctx: Context, trade: TradeRequest):
        """Envoie le résultat du trade au Logger."""
        try:
            # Adresse du Logger (à configurer)
            logger_address = "agent1q2kxac3lxe4f9m9h2p9jwzqrv2y6s8ll0ctus7"
            
            await ctx.send(logger_address, trade)
            logger.info("Résultat envoyé au Logger", 
                       trade_id=trade.trade_id,
                       symbol=trade.symbol)
            
        except Exception as e:
            logger.error("Erreur envoi au Logger", error=str(e))
    
    async def handle_price_update(self, ctx: Context, sender: str, msg: Prediction):
        """Gère les mises à jour de prix pour les stop loss/take profit."""
        try:
            current_price = msg.features_used.get("current_price", 0)
            symbol = msg.symbol
            
            if symbol in self.open_trades:
                trade_info = self.open_trades[symbol]
                
                # Vérification du stop loss
                if current_price <= trade_info["stop_loss"]:
                    await self._close_trade(symbol, current_price, "stop_loss")
                
                # Vérification du take profit
                elif current_price >= trade_info["take_profit"]:
                    await self._close_trade(symbol, current_price, "take_profit")
            
        except Exception as e:
            logger.error("Erreur mise à jour prix", error=str(e))
    
    async def _close_trade(self, symbol: str, exit_price: float, reason: str):
        """Ferme un trade ouvert."""
        try:
            trade_info = self.open_trades[symbol]
            entry_price = trade_info["entry_price"]
            quantity = trade_info["quantity"]
            
            # Calcul du P&L
            if trade_info.get("side") == SignalType.BUY:
                pnl = (exit_price - entry_price) * quantity * self.capital
            else:
                pnl = (entry_price - exit_price) * quantity * self.capital
            
            # Mise à jour du capital
            self.available_capital += quantity * exit_price * self.capital
            self.total_pnl += pnl
            
            if pnl > 0:
                self.successful_trades += 1
            
            # Suppression du trade ouvert
            del self.open_trades[symbol]
            
            logger.info("Trade fermé", 
                       symbol=symbol,
                       reason=reason,
                       pnl=pnl,
                       total_pnl=self.total_pnl)
            
        except Exception as e:
            logger.error("Erreur fermeture trade", 
                        symbol=symbol,
                        error=str(e))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques de trading."""
        win_rate = (self.successful_trades / self.total_trades * 100) if self.total_trades > 0 else 0
        
        return {
            "total_trades": self.total_trades,
            "successful_trades": self.successful_trades,
            "win_rate": round(win_rate, 2),
            "total_pnl": round(self.total_pnl, 2),
            "available_capital": round(self.available_capital, 2),
            "open_trades": len(self.open_trades)
        }
    
    async def run(self):
        """Démarre l'agent Trader."""
        logger.info("🚀 Démarrage du TraderAgent...")
        
        # Financement de l'agent si nécessaire
        await fund_agent_if_low(self.wallet.address())
        
        # Démarrage de l'agent
        await super().run()

if __name__ == "__main__":
    agent = TraderAgent()
    asyncio.run(agent.run())
