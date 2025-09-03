"""Agent Logger - Monitoring et feedback du pipeline de trading."""

import asyncio
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

from ..models.trade import TradeRequest, TradeStatus
from ..models.prediction import Prediction
from ..models.signal import Signal

logger = structlog.get_logger(__name__)

class LoggerAgent(Agent):
    """Agent Logger pour le monitoring et feedback du pipeline."""
    
    def __init__(self):
        super().__init__(
            name="LoggerAgent",
            port=9005,
            seed="logger_seed_12345",
            endpoint=["http://127.0.0.1:9005/submit"]
        )
        
        # Configuration du monitoring
        self.monitoring_config = {
            "log_retention_days": 30,
            "alert_threshold_execution_rate": 0.7,  # 70% de succès
            "alert_threshold_confidence": 0.5,      # 50% de confiance
            "performance_update_interval": 300      # 5 minutes
        }
        
        # Données de monitoring du pipeline
        self.pipeline_logs: List[Dict[str, Any]] = []
        self.market_data_logs: List[Dict[str, Any]] = []
        self.prediction_logs: List[Dict[str, Any]] = []
        self.strategy_logs: List[Dict[str, Any]] = []
        self.trader_logs: List[Dict[str, Any]] = []
        
        # Alertes basées sur les vraies données
        self.alerts: List[Dict[str, Any]] = []
        self.max_alerts = 100
        
        # Statistiques en temps réel basées sur les vraies données
        self.pipeline_stats = {
            "total_executions": 0,
            "successful_executions": 0,
            "execution_rate": 0.0,
            "data_collection_success": 0,
            "prediction_accuracy": 0.0,
            "signal_generation_rate": 0.0,
            "trade_execution_rate": 0.0,
            "last_execution": None,
            "pipeline_health": "Unknown"
        }
        
        # Configuration des handlers pour recevoir les vraies données
        self.on_message(model=TradeRequest)(self.handle_trade_result)
        self.on_message(model=Prediction)(self.handle_prediction)
        self.on_message(model=Signal)(self.handle_signal)
        
        # Tâche périodique pour analyser la santé du pipeline
        self.health_check_task = self.on_interval(period=300)(self.analyze_pipeline_health)
        
        logger.info("LoggerAgent initialisé pour monitoring du pipeline", 
                   monitoring_config=self.monitoring_config)
    
    async def handle_trade_result(self, ctx: Context, sender: str, msg: TradeRequest):
        """Traite les résultats de trading pour le monitoring."""
        try:
            logger.info("📊 Résultat de trade reçu", 
                       trade_id=msg.trade_id,
                       symbol=msg.symbol,
                       status=msg.status.value,
                       pnl=msg.realized_pnl)
            
            # Enregistrement du trade
            trade_log = {
                "trade_id": msg.trade_id,
                "symbol": msg.symbol,
                "side": msg.side.value,
                "quantity": msg.quantity,
                "entry_price": msg.price,
                "exit_price": msg.price,  # À ajuster selon le statut
                "status": msg.status.value,
                "realized_pnl": msg.realized_pnl or 0.0,
                "timestamp": msg.timestamp,
                "signal_data": msg.signal_data
            }
            
            self.trade_logs.append(trade_log)
            
            # Mise à jour des statistiques
            await self._update_statistics(trade_log)
            
            # Vérification des alertes
            await self._check_alerts()
            
            # Feedback au Predictor si nécessaire
            if msg.signal_data:
                await self._send_feedback_to_predictor(ctx, msg)
            
            logger.info("Trade enregistré et statistiques mises à jour")
            
        except Exception as e:
            logger.error("❌ Erreur traitement résultat trade", 
                        trade_id=msg.trade_id,
                        error=str(e))
    
    async def handle_prediction(self, ctx: Context, sender: str, msg: Prediction):
        """Enregistre les prédictions pour analyse."""
        try:
            prediction_log = {
                "symbol": msg.symbol,
                "direction_prob": msg.direction_prob,
                "confidence": msg.confidence,
                "volatility": msg.volatility,
                "model_name": msg.model_name,
                "features_used": msg.features_used,
                "timestamp": msg.timestamp
            }
            
            self.prediction_logs.append(prediction_log)
            
            # Limiter la taille des logs
            if len(self.prediction_logs) > 1000:
                self.prediction_logs = self.prediction_logs[-1000:]
            
            logger.debug("Prédiction enregistrée", symbol=msg.symbol)
            
        except Exception as e:
            logger.error("Erreur enregistrement prédiction", error=str(e))
    
    async def handle_signal(self, ctx: Context, sender: str, msg: Signal):
        """Enregistre les signaux pour analyse."""
        try:
            signal_log = {
                "symbol": msg.symbol,
                "signal_type": msg.signal_type.value,
                "confidence": msg.confidence,
                "price": msg.price,
                "position_size": msg.position_size,
                "stop_loss": msg.stop_loss,
                "take_profit": msg.take_profit,
                "timestamp": msg.timestamp
            }
            
            self.signal_logs.append(signal_log)
            
            # Limiter la taille des logs
            if len(self.signal_logs) > 1000:
                self.signal_logs = self.signal_logs[-1000:]
            
            logger.debug("Signal enregistré", 
                        symbol=msg.symbol,
                        signal_type=msg.signal_type.value)
            
        except Exception as e:
            logger.error("Erreur enregistrement signal", error=str(e))
    
    async def _update_pipeline_statistics(self, data: Dict[str, Any]):
        """Met à jour les statistiques du pipeline basées sur les vraies données."""
        try:
            # Mise à jour des compteurs d'exécution
            self.pipeline_stats["total_executions"] += 1
            
            # Vérifier la qualité des données collectées
            if data.get("price") and data.get("symbol"):
                self.pipeline_stats["data_collection_success"] += 1
            
            # Vérifier la qualité des prédictions
            if data.get("prediction") and data.get("prediction", {}).get("confidence", 0) > 0:
                self.pipeline_stats["prediction_accuracy"] += 1
            
            # Vérifier la génération de signaux
            if data.get("strategy_signal"):
                self.pipeline_stats["signal_generation_rate"] += 1
            
            # Vérifier l'exécution des trades
            if data.get("trade_execution"):
                self.pipeline_stats["trade_execution_rate"] += 1
            
            # Calculer les taux de succès
            if self.pipeline_stats["total_executions"] > 0:
                self.pipeline_stats["execution_rate"] = (
                    self.pipeline_stats["data_collection_success"] / self.pipeline_stats["total_executions"]
                )
            
            # Mise à jour du timestamp de dernière exécution
            self.pipeline_stats["last_execution"] = data.get("timestamp", datetime.utcnow())
            
            # Évaluer la santé du pipeline
            await self._evaluate_pipeline_health()
            
            logger.info("Statistiques du pipeline mises à jour", 
                       total_executions=self.pipeline_stats["total_executions"],
                       execution_rate=self.pipeline_stats["execution_rate"],
                       pipeline_health=self.pipeline_stats["pipeline_health"])
            
        except Exception as e:
            logger.error("Erreur mise à jour statistiques pipeline", error=str(e))
    
    async def _calculate_drawdown(self):
        """Calcule le drawdown actuel et maximum."""
        try:
            if len(self.trade_logs) < 2:
                return
            
            # Calcul du drawdown
            cumulative_pnl = 0.0
            peak_pnl = 0.0
            current_drawdown = 0.0
            max_drawdown = 0.0
            
            for trade in self.trade_logs:
                cumulative_pnl += trade["realized_pnl"]
                
                if cumulative_pnl > peak_pnl:
                    peak_pnl = cumulative_pnl
                
                current_drawdown = peak_pnl - cumulative_pnl
                
                if current_drawdown > max_drawdown:
                    max_drawdown = current_drawdown
            
            self.stats["current_drawdown"] = current_drawdown
            self.stats["max_drawdown"] = max_drawdown
            
        except Exception as e:
            logger.error("Erreur calcul drawdown", error=str(e))
    
    async def _check_alerts(self):
        """Vérifie et génère des alertes si nécessaire."""
        try:
            # Alerte P&L négatif
            if self.stats["total_pnl"] < self.monitoring_config["alert_threshold_pnl"]:
                alert = {
                    "type": "pnl_alert",
                    "message": f"P&L total négatif: ${self.stats['total_pnl']:.2f}",
                    "severity": "high",
                    "timestamp": datetime.utcnow()
                }
                self._add_alert(alert)
            
            # Alerte win rate faible
            if self.stats["win_rate"] < self.monitoring_config["alert_threshold_winrate"]:
                alert = {
                    "type": "winrate_alert",
                    "message": f"Win rate faible: {self.stats['win_rate']*100:.1f}%",
                    "severity": "medium",
                    "timestamp": datetime.utcnow()
                }
                self._add_alert(alert)
            
            # Alerte drawdown élevé
            if self.stats["current_drawdown"] > 500:  # 500 USD
                alert = {
                    "type": "drawdown_alert",
                    "message": f"Drawdown élevé: ${self.stats['current_drawdown']:.2f}",
                    "severity": "high",
                    "timestamp": datetime.utcnow()
                }
                self._add_alert(alert)
            
        except Exception as e:
            logger.error("Erreur vérification alertes", error=str(e))
    
    def _add_alert(self, alert: Dict[str, Any]):
        """Ajoute une alerte à la liste."""
        self.alerts.append(alert)
        
        # Limiter le nombre d'alertes
        if len(self.alerts) > self.max_alerts:
            self.alerts = self.alerts[-self.max_alerts:]
        
        logger.warning("Alerte générée", 
                      type=alert["type"],
                      message=alert["message"],
                      severity=alert["severity"])
    
    async def _send_feedback_to_predictor(self, ctx: Context, trade: TradeRequest):
        """Envoie un feedback au Predictor pour améliorer le modèle."""
        try:
            # Analyse de la performance de la prédiction
            if trade.signal_data:
                signal = trade.signal_data
                prediction_accuracy = self._calculate_prediction_accuracy(signal, trade)
                
                # Feedback basé sur l'accuracy
                feedback = {
                    "symbol": trade.symbol,
                    "prediction_accuracy": prediction_accuracy,
                    "actual_pnl": trade.realized_pnl or 0.0,
                    "expected_direction": signal.get("signal_type"),
                    "actual_direction": "BUY" if trade.realized_pnl > 0 else "SELL",
                    "timestamp": datetime.utcnow()
                }
                
                # Envoi au Predictor (adresse à configurer)
                predictor_address = "agent1q2kxac3lxe4f9m9h2p9jwzqrv2y6s8ll0ctus7"
                
                await ctx.send(predictor_address, feedback)
                
                logger.info("Feedback envoyé au Predictor", 
                           symbol=trade.symbol,
                           accuracy=prediction_accuracy)
            
        except Exception as e:
            logger.error("Erreur envoi feedback", error=str(e))
    
    def _calculate_prediction_accuracy(self, signal: Dict[str, Any], trade: TradeRequest) -> float:
        """Calcule l'accuracy de la prédiction."""
        try:
            # Logique simple : si le P&L est positif, la prédiction était correcte
            if trade.realized_pnl and trade.realized_pnl > 0:
                return 1.0
            elif trade.realized_pnl and trade.realized_pnl < 0:
                return 0.0
            else:
                return 0.5  # Neutre si P&L = 0
            
        except Exception as e:
            logger.error("Erreur calcul accuracy", error=str(e))
            return 0.5
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Génère un rapport de performance complet."""
        try:
            # Calculs supplémentaires
            avg_trade_pnl = (
                self.stats["total_pnl"] / self.stats["total_trades"]
                if self.stats["total_trades"] > 0 else 0.0
            )
            
            # Performance par symbole
            symbol_performance = {}
            for trade in self.trade_logs:
                symbol = trade["symbol"]
                if symbol not in symbol_performance:
                    symbol_performance[symbol] = {
                        "trades": 0,
                        "pnl": 0.0,
                        "wins": 0
                    }
                
                symbol_performance[symbol]["trades"] += 1
                symbol_performance[symbol]["pnl"] += trade["realized_pnl"]
                if trade["realized_pnl"] > 0:
                    symbol_performance[symbol]["wins"] += 1
            
            # Calcul des win rates par symbole
            for symbol in symbol_performance:
                perf = symbol_performance[symbol]
                perf["win_rate"] = (
                    perf["wins"] / perf["trades"] * 100
                    if perf["trades"] > 0 else 0.0
                )
            
            return {
                "summary": {
                    "total_trades": self.stats["total_trades"],
                    "successful_trades": self.stats["successful_trades"],
                    "win_rate": round(self.stats["win_rate"] * 100, 2),
                    "total_pnl": round(self.stats["total_pnl"], 2),
                    "avg_trade_pnl": round(avg_trade_pnl, 2),
                    "best_trade": round(self.stats["best_trade"], 2),
                    "worst_trade": round(self.stats["worst_trade"], 2),
                    "current_drawdown": round(self.stats["current_drawdown"], 2),
                    "max_drawdown": round(self.stats["max_drawdown"], 2)
                },
                "symbol_performance": symbol_performance,
                "recent_alerts": self.alerts[-10:],  # 10 dernières alertes
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Erreur génération rapport", error=str(e))
            return {}
    
    async def _evaluate_pipeline_health(self):
        """Évalue la santé globale du pipeline basée sur les vraies données."""
        try:
            if self.pipeline_stats["total_executions"] == 0:
                self.pipeline_stats["pipeline_health"] = "Unknown"
                return
            
            # Calculer le score de santé (0-100)
            health_score = 0
            
            # Données de marché (30% du score)
            data_score = (self.pipeline_stats["data_collection_success"] / self.pipeline_stats["total_executions"]) * 30
            health_score += data_score
            
            # Prédictions (25% du score)
            if self.pipeline_stats["prediction_accuracy"] > 0:
                prediction_score = (self.pipeline_stats["prediction_accuracy"] / self.pipeline_stats["total_executions"]) * 25
                health_score += prediction_score
            
            # Signaux (25% du score)
            if self.pipeline_stats["signal_generation_rate"] > 0:
                signal_score = (self.pipeline_stats["signal_generation_rate"] / self.pipeline_stats["total_executions"]) * 25
                health_score += signal_score
            
            # Trades (20% du score)
            if self.pipeline_stats["trade_execution_rate"] > 0:
                trade_score = (self.pipeline_stats["trade_execution_rate"] / self.pipeline_stats["total_executions"]) * 20
                health_score += trade_score
            
            # Définir la santé du pipeline
            if health_score >= 80:
                self.pipeline_stats["pipeline_health"] = "Excellent"
            elif health_score >= 60:
                self.pipeline_stats["pipeline_health"] = "Good"
            elif health_score >= 40:
                self.pipeline_stats["pipeline_health"] = "Fair"
            else:
                self.pipeline_stats["pipeline_health"] = "Poor"
            
            # Vérifier les alertes
            await self._check_pipeline_alerts(health_score)
            
            logger.info("Santé du pipeline évaluée", 
                       health_score=round(health_score, 1),
                       pipeline_health=self.pipeline_stats["pipeline_health"])
            
        except Exception as e:
            logger.error("Erreur évaluation santé pipeline", error=str(e))
    
    async def _check_pipeline_alerts(self, health_score: float):
        """Vérifie et génère des alertes basées sur la santé du pipeline."""
        try:
            # Alerte si le taux d'exécution est faible
            if self.pipeline_stats["execution_rate"] < self.monitoring_config["alert_threshold_execution_rate"]:
                alert = {
                    "type": "LOW_EXECUTION_RATE",
                    "message": f"Taux d'exécution faible: {self.pipeline_stats['execution_rate']:.1%}",
                    "severity": "WARNING",
                    "timestamp": datetime.utcnow().isoformat(),
                    "recommendation": "Vérifier la connectivité des agents et la qualité des données"
                }
                self._add_alert(alert)
            
            # Alerte si la santé globale est mauvaise
            if health_score < 40:
                alert = {
                    "type": "POOR_PIPELINE_HEALTH",
                    "message": f"Santé du pipeline dégradée: {self.pipeline_stats['pipeline_health']}",
                    "severity": "CRITICAL",
                    "timestamp": datetime.utcnow().isoformat(),
                    "recommendation": "Arrêter le pipeline et diagnostiquer les problèmes"
                }
                self._add_alert(alert)
            
            # Alerte si pas d'exécution récente
            if (self.pipeline_stats["last_execution"] and 
                (datetime.utcnow() - self.pipeline_stats["last_execution"]).total_seconds() > 300):
                alert = {
                    "type": "NO_RECENT_EXECUTION",
                    "message": "Aucune exécution du pipeline depuis plus de 5 minutes",
                    "severity": "WARNING",
                    "timestamp": datetime.utcnow().isoformat(),
                    "recommendation": "Vérifier que le pipeline est actif"
                }
                self._add_alert(alert)
                
        except Exception as e:
            logger.error("Erreur vérification alertes pipeline", error=str(e))
    
    def _add_alert(self, alert: Dict[str, Any]):
        """Ajoute une alerte à la liste."""
        if len(self.alerts) >= self.max_alerts:
            self.alerts.pop(0)  # Supprimer la plus ancienne
        self.alerts.append(alert)
    
    async def analyze_pipeline_health(self, ctx: Context):
        """Analyse périodique de la santé du pipeline."""
        try:
            logger.info("🔍 Analyse de la santé du pipeline...")
            
            # Générer un rapport de santé
            health_report = {
                "timestamp": datetime.utcnow().isoformat(),
                "pipeline_stats": self.pipeline_stats,
                "recent_alerts": self.alerts[-5:] if self.alerts else [],
                "recommendations": self._generate_recommendations()
            }
            
            logger.info("📊 Rapport de santé du pipeline généré", 
                       health_score=self.pipeline_stats["pipeline_health"],
                       total_alerts=len(self.alerts))
            
        except Exception as e:
            logger.error("❌ Erreur analyse santé pipeline", error=str(e))
    
    def _generate_recommendations(self) -> List[str]:
        """Génère des recommandations basées sur l'état du pipeline."""
        recommendations = []
        
        if self.pipeline_stats["execution_rate"] < 0.7:
            recommendations.append("Améliorer la qualité des données de marché")
        
        if self.pipeline_stats["prediction_accuracy"] < 0.5:
            recommendations.append("Optimiser les modèles de prédiction")
        
        if self.pipeline_stats["signal_generation_rate"] < 0.6:
            recommendations.append("Revoir la logique de génération de signaux")
        
        if not recommendations:
            recommendations.append("Pipeline fonctionne correctement")
        
        return recommendations
    
    async def run(self):
        """Démarre l'agent Logger."""
        logger.info("🚀 Démarrage du LoggerAgent...")
        
        # Financement de l'agent si nécessaire
        await fund_agent_if_low(self.wallet.address())
        
        # Démarrage de l'agent
        await super().run()

if __name__ == "__main__":
    agent = LoggerAgent()
    asyncio.run(agent.run())
