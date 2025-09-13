#!/usr/bin/env python3
"""
Pipeline Manager - Orchestration séquentielle des agents de trading
"""

import asyncio
import structlog
import threading
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from ..agents.trading.data_collector import DataCollectorAgent
from ..agents.trading.news_collector import NewsCollectorAgent
from ..agents.trading.data_aggregator import DataAggregatorAgent
from ..agents.trading.predictor import PredictorAgent
from ..agents.trading.strategy import StrategyAgent
from ..agents.trading.trader import TraderAgent
from ..agents.trading.logger import LoggerAgent

logger = structlog.get_logger(__name__)

class AgentStatus(Enum):
    """Statuts possibles d'un agent."""
    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"
    PROCESSING = "processing"

@dataclass
class AgentInfo:
    """Informations sur un agent."""
    name: str
    status: AgentStatus
    last_execution: Optional[datetime] = None
    execution_count: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    processing_time_ms: Optional[int] = None

@dataclass
class PipelineData:
    """Données qui passent entre les agents."""
    timestamp: datetime
    symbol: str
    price: float
    volume: float
    prediction: Optional[Dict[str, Any]] = None
    strategy_signal: Optional[Dict[str, Any]] = None
    trade_execution: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class PipelineManager:
    """Gestionnaire du pipeline séquentiel des agents."""
    
    def __init__(self):
        self.agents: Dict[str, Any] = {}
        self.agent_status: Dict[str, AgentInfo] = {}
        self.pipeline_data: List[PipelineData] = []
        self.is_running = False
        self.execution_interval = 60  # secondes
        self.max_pipeline_data = 1000
        self.pipeline_thread = None
        self.stop_event = threading.Event()
        
        # Initialisation des agents
        self._init_agents()
        
    def _init_agents(self):
        """Initialise tous les agents du pipeline."""
        try:
            logger.info("🚀 Initialisation des agents du pipeline...")
            
            # Création des agents dans l'ordre du pipeline
            self.agents = {
                "data_collector": DataCollectorAgent(),
                "news_collector": NewsCollectorAgent(),
                "data_aggregator": DataAggregatorAgent(),
                "predictor": PredictorAgent(),
                "strategy": StrategyAgent(),
                "trader": TraderAgent(),
                "logger": LoggerAgent()
            }
            
            # Initialisation des statuts
            for name in self.agents.keys():
                self.agent_status[name] = AgentInfo(
                    name=name,
                    status=AgentStatus.STOPPED
                )
            
            logger.info("✅ Tous les agents initialisés", 
                       agents=list(self.agents.keys()))
            
        except Exception as e:
            logger.error("❌ Erreur initialisation agents", error=str(e))
            raise
    
    async def start_pipeline(self):
        """Démarre le pipeline complet."""
        if self.is_running:
            logger.warning("⚠️ Pipeline déjà en cours d'exécution")
            return False
        
        try:
            logger.info("🚀 Démarrage du pipeline séquentiel...")
            self.is_running = True
            self.stop_event.clear()
            
            # Démarrer la tâche périodique dans un thread séparé
            self.pipeline_thread = threading.Thread(target=self._pipeline_loop_thread, daemon=True)
            self.pipeline_thread.start()
            
            logger.info("✅ Pipeline démarré avec succès")
            return True
            
        except Exception as e:
            logger.error("❌ Erreur démarrage pipeline", error=str(e))
            self.is_running = False
            return False
    
    async def stop_pipeline(self):
        """Arrête le pipeline complet."""
        if not self.is_running:
            logger.warning("⚠️ Pipeline déjà arrêté")
            return False
        
        try:
            logger.info("🛑 Arrêt du pipeline...")
            self.is_running = False
            self.stop_event.set()
            
            # Attendre que le thread se termine
            if self.pipeline_thread and self.pipeline_thread.is_alive():
                self.pipeline_thread.join(timeout=5)
            
            # Arrêter tous les agents
            for name, agent in self.agents.items():
                if hasattr(agent, 'stop'):
                    await agent.stop()
                self.agent_status[name].status = AgentStatus.STOPPED
            
            logger.info("✅ Pipeline arrêté")
            return True
            
        except Exception as e:
            logger.error("❌ Erreur arrêt pipeline", error=str(e))
            return False
    
    def _pipeline_loop_thread(self):
        """Boucle principale du pipeline dans un thread séparé."""
        logger.info("🔄 Démarrage de la boucle pipeline dans le thread")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                start_time = datetime.utcnow()
                logger.info("🔄 Début cycle pipeline", timestamp=start_time)
                
                # Exécution séquentielle des agents (version synchrone)
                pipeline_data = self._execute_pipeline_sequence_sync()
                
                if pipeline_data:
                    self.pipeline_data.append(pipeline_data)
                    # Garder seulement les dernières données
                    if len(self.pipeline_data) > self.max_pipeline_data:
                        self.pipeline_data = self.pipeline_data[-self.max_pipeline_data:]
                
                # Calculer le temps d'exécution
                execution_time = (datetime.utcnow() - start_time).total_seconds()
                logger.info("✅ Cycle pipeline terminé", 
                           execution_time_seconds=execution_time,
                           pipeline_data_count=len(self.pipeline_data))
                
                # Attendre le prochain cycle (version thread-safe)
                for _ in range(self.execution_interval):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
                
            except Exception as e:
                logger.error("❌ Erreur dans la boucle pipeline", error=str(e))
                # Attendre 10 secondes avant de réessayer
                for _ in range(10):
                    if self.stop_event.is_set():
                        break
                    time.sleep(1)
        
        logger.info("🛑 Boucle pipeline terminée")
    
    async def _pipeline_loop(self):
        """Boucle principale du pipeline (version asynchrone pour compatibilité)."""
        # Cette méthode est maintenant dépréciée, utilisez _pipeline_loop_thread
        logger.warning("⚠️ _pipeline_loop est déprécié, utilisez _pipeline_loop_thread")
        return await self._execute_pipeline_sequence()
    
    async def _execute_pipeline_sequence(self) -> Optional[PipelineData]:
        """Exécute la séquence complète des agents."""
        try:
            # 1. DataCollector - Collecte des données
            logger.info("📊 Étape 1: DataCollector")
            market_data = await self._execute_data_collector()
            if not market_data:
                logger.warning("⚠️ Aucune donnée collectée, arrêt du pipeline")
                return None
            
            # 2. Predictor - Génération de prédictions
            logger.info("🔮 Étape 2: Predictor")
            prediction = await self._execute_predictor(market_data)
            
            # 3. Strategy - Analyse et signaux
            logger.info("📈 Étape 3: Strategy")
            strategy_signal = await self._execute_strategy(market_data, prediction)
            
            # 4. Trader - Exécution des trades
            logger.info("💰 Étape 4: Trader")
            trade_execution = await self._execute_trader(market_data, strategy_signal)
            
            # 5. Logger - Monitoring et logging
            logger.info("📝 Étape 5: Logger")
            await self._execute_logger(market_data, prediction, strategy_signal, trade_execution)
            
            # Créer les données du pipeline
            pipeline_data = PipelineData(
                timestamp=datetime.utcnow(),
                symbol=market_data.get("symbol", "UNKNOWN"),
                price=market_data.get("price", 0.0),
                volume=market_data.get("volume", 0.0),
                prediction=prediction,
                strategy_signal=strategy_signal,
                trade_execution=trade_execution,
                metadata={
                    "pipeline_version": "1.0.0",
                    "execution_id": f"exec_{datetime.utcnow().timestamp()}"
                }
            )
            
            return pipeline_data
            
        except Exception as e:
                    logger.error("❌ Erreur dans la séquence pipeline", error=str(e))
        return None
    
    def _execute_pipeline_sequence_sync(self) -> Optional[PipelineData]:
        """Exécute la séquence complète des agents (version synchrone pour le thread)."""
        try:
            # 1. DataCollector - Collecte des données
            logger.info("📊 Étape 1: DataCollector")
            market_data = self._execute_data_collector_sync()
            if not market_data:
                logger.warning("⚠️ Aucune donnée collectée, arrêt du pipeline")
                return None
            
            # 2. Predictor - Génération de prédictions
            logger.info("🔮 Étape 2: Predictor")
            prediction = self._execute_predictor_sync(market_data)
            
            # 3. Strategy - Analyse et signaux
            logger.info("📈 Étape 3: Strategy")
            strategy_signal = self._execute_strategy_sync(market_data, prediction)
            
            # 4. Trader - Exécution des trades
            logger.info("💰 Étape 4: Trader")
            trade_execution = self._execute_trader_sync(market_data, strategy_signal)
            
            # 5. Logger - Monitoring et logging
            logger.info("📝 Étape 5: Logger")
            self._execute_logger_sync(market_data, prediction, strategy_signal, trade_execution)
            
            # Créer les données du pipeline
            pipeline_data = PipelineData(
                timestamp=datetime.utcnow(),
                symbol=market_data.get("symbol", "UNKNOWN"),
                price=market_data.get("price", 0.0),
                volume=market_data.get("volume", 0.0),
                prediction=prediction,
                strategy_signal=strategy_signal,
                trade_execution=trade_execution,
                metadata={
                    "pipeline_version": "1.0.0",
                    "execution_id": f"exec_{datetime.utcnow().timestamp()}"
                }
            )
            
            return pipeline_data
            
        except Exception as e:
            logger.error("❌ Erreur dans la séquence pipeline synchrone", error=str(e))
            return None
    
    async def _execute_data_collector(self) -> Optional[Dict[str, Any]]:
        """Exécute l'agent DataCollector."""
        agent_name = "data_collector"
        start_time = datetime.utcnow()
        
        try:
            self.agent_status[agent_name].status = AgentStatus.PROCESSING
            
            # Simuler la collecte de données (remplacé par l'appel réel à l'agent)
            market_data = {
                "symbol": "BTC/USD",
                "price": 108538.0,
                "volume": 1000000.0,
                "timestamp": datetime.utcnow(),
                "source": "CoinGecko"
            }
            
            # Mettre à jour le statut
            self.agent_status[agent_name].status = AgentStatus.RUNNING
            self.agent_status[agent_name].last_execution = datetime.utcnow()
            self.agent_status[agent_name].execution_count += 1
            self.agent_status[agent_name].processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            logger.info("✅ DataCollector exécuté", data=market_data)
            return market_data
            
        except Exception as e:
            self.agent_status[agent_name].status = AgentStatus.ERROR
            self.agent_status[agent_name].error_count += 1
            self.agent_status[agent_name].last_error = str(e)
            logger.error("❌ Erreur DataCollector", error=str(e))
            return None
    
    def _execute_data_collector_sync(self) -> Optional[Dict[str, Any]]:
        """Exécute l'agent DataCollector (version synchrone)."""
        agent_name = "data_collector"
        start_time = datetime.utcnow()
        
        try:
            self.agent_status[agent_name].status = AgentStatus.PROCESSING
            
            # Simuler la collecte de données (remplacé par l'appel réel à l'agent)
            market_data = {
                "symbol": "BTC/USD",
                "price": 108538.0,
                "volume": 1000000.0,
                "timestamp": datetime.utcnow(),
                "source": "CoinGecko"
            }
            
            # Mettre à jour le statut
            self.agent_status[agent_name].status = AgentStatus.RUNNING
            self.agent_status[agent_name].last_execution = datetime.utcnow()
            self.agent_status[agent_name].execution_count += 1
            self.agent_status[agent_name].processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            logger.info("✅ DataCollector exécuté (sync)", data=market_data)
            return market_data
            
        except Exception as e:
            self.agent_status[agent_name].status = AgentStatus.ERROR
            self.agent_status[agent_name].error_count += 1
            self.agent_status[agent_name].last_error = str(e)
            logger.error("❌ Erreur DataCollector (sync)", error=str(e))
            return None
    
    async def _execute_predictor(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Exécute l'agent Predictor."""
        agent_name = "predictor"
        start_time = datetime.utcnow()
        
        try:
            self.agent_status[agent_name].status = AgentStatus.PROCESSING
            
            # Simuler la prédiction (remplacé par l'appel réel à l'agent)
            prediction = {
                "direction": "UP",
                "confidence": 0.75,
                "price_target": market_data["price"] * 1.02,
                "timestamp": datetime.utcnow()
            }
            
            # Mettre à jour le statut
            self.agent_status[agent_name].status = AgentStatus.RUNNING
            self.agent_status[agent_name].last_execution = datetime.utcnow()
            self.agent_status[agent_name].execution_count += 1
            self.agent_status[agent_name].processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            logger.info("✅ Predictor exécuté", prediction=prediction)
            return prediction
            
        except Exception as e:
            self.agent_status[agent_name].status = AgentStatus.ERROR
            self.agent_status[agent_name].error_count += 1
            self.agent_status[agent_name].last_error = str(e)
            logger.error("❌ Erreur Predictor", error=str(e))
            return None
    
    def _execute_predictor_sync(self, market_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Exécute l'agent Predictor (version synchrone)."""
        agent_name = "predictor"
        start_time = datetime.utcnow()
        
        try:
            self.agent_status[agent_name].status = AgentStatus.PROCESSING
            
            # Simuler la prédiction (remplacé par l'appel réel à l'agent)
            prediction = {
                "direction": "UP",
                "confidence": 0.75,
                "price_target": market_data["price"] * 1.02,
                "timestamp": datetime.utcnow()
            }
            
            # Mettre à jour le statut
            self.agent_status[agent_name].status = AgentStatus.RUNNING
            self.agent_status[agent_name].last_execution = datetime.utcnow()
            self.agent_status[agent_name].execution_count += 1
            self.agent_status[agent_name].processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            logger.info("✅ Predictor exécuté (sync)", prediction=prediction)
            return prediction
            
        except Exception as e:
            self.agent_status[agent_name].status = AgentStatus.ERROR
            self.agent_status[agent_name].error_count += 1
            self.agent_status[agent_name].last_error = str(e)
            logger.error("❌ Erreur Predictor (sync)", error=str(e))
            return None
    
    async def _execute_strategy(self, market_data: Dict[str, Any], prediction: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Exécute l'agent Strategy."""
        agent_name = "strategy"
        start_time = datetime.utcnow()
        
        try:
            self.agent_status[agent_name].status = AgentStatus.PROCESSING
            
            # Simuler la stratégie (remplacé par l'appel réel à l'agent)
            strategy_signal = {
                "action": "BUY" if prediction and prediction.get("direction") == "UP" else "HOLD",
                "confidence": prediction.get("confidence", 0.5) if prediction else 0.5,
                "position_size": 0.1,
                "stop_loss": market_data["price"] * 0.98,
                "take_profit": market_data["price"] * 1.05,
                "timestamp": datetime.utcnow()
            }
            
            # Mettre à jour le statut
            self.agent_status[agent_name].status = AgentStatus.RUNNING
            self.agent_status[agent_name].last_execution = datetime.utcnow()
            self.agent_status[agent_name].execution_count += 1
            self.agent_status[agent_name].processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            logger.info("✅ Strategy exécuté", signal=strategy_signal)
            return strategy_signal
            
        except Exception as e:
            self.agent_status[agent_name].status = AgentStatus.ERROR
            self.agent_status[agent_name].error_count += 1
            self.agent_status[agent_name].last_error = str(e)
            logger.error("❌ Erreur Strategy", error=str(e))
            return None
    
    def _execute_strategy_sync(self, market_data: Dict[str, Any], prediction: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Exécute l'agent Strategy (version synchrone)."""
        agent_name = "strategy"
        start_time = datetime.utcnow()
        
        try:
            self.agent_status[agent_name].status = AgentStatus.PROCESSING
            
            # Simuler la stratégie (remplacé par l'appel réel à l'agent)
            strategy_signal = {
                "action": "BUY" if prediction and prediction.get("direction") == "UP" else "HOLD",
                "confidence": prediction.get("confidence", 0.5) if prediction else 0.5,
                "position_size": 0.1,
                "stop_loss": market_data["price"] * 0.98,
                "take_profit": market_data["price"] * 1.05,
                "timestamp": datetime.utcnow()
            }
            
            # Mettre à jour le statut
            self.agent_status[agent_name].status = AgentStatus.RUNNING
            self.agent_status[agent_name].last_execution = datetime.utcnow()
            self.agent_status[agent_name].execution_count += 1
            self.agent_status[agent_name].processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            logger.info("✅ Strategy exécuté (sync)", signal=strategy_signal)
            return strategy_signal
            
        except Exception as e:
            self.agent_status[agent_name].status = AgentStatus.ERROR
            self.agent_status[agent_name].error_count += 1
            self.agent_status[agent_name].last_error = str(e)
            logger.error("❌ Erreur Strategy (sync)", error=str(e))
            return None
    
    async def _execute_trader(self, market_data: Dict[str, Any], strategy_signal: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Exécute l'agent Trader."""
        agent_name = "trader"
        start_time = datetime.utcnow()
        
        try:
            self.agent_status[agent_name].status = AgentStatus.PROCESSING
            
            # Simuler l'exécution du trade (remplacé par l'appel réel à l'agent)
            trade_execution = None
            if strategy_signal and strategy_signal.get("action") != "HOLD":
                trade_execution = {
                    "trade_id": f"trade_{datetime.utcnow().timestamp()}",
                    "action": strategy_signal["action"],
                    "quantity": strategy_signal["position_size"],
                    "price": market_data["price"],
                    "status": "FILLED",
                    "timestamp": datetime.utcnow()
                }
            
            # Mettre à jour le statut
            self.agent_status[agent_name].status = AgentStatus.RUNNING
            self.agent_status[agent_name].last_execution = datetime.utcnow()
            self.agent_status[agent_name].execution_count += 1
            self.agent_status[agent_name].processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            logger.info("✅ Trader exécuté", trade=trade_execution)
            return trade_execution
            
        except Exception as e:
            self.agent_status[agent_name].status = AgentStatus.ERROR
            self.agent_status[agent_name].error_count += 1
            self.agent_status[agent_name].last_error = str(e)
            logger.error("❌ Erreur Trader", error=str(e))
            return None
    
    def _execute_trader_sync(self, market_data: Dict[str, Any], strategy_signal: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Exécute l'agent Trader (version synchrone)."""
        agent_name = "trader"
        start_time = datetime.utcnow()
        
        try:
            self.agent_status[agent_name].status = AgentStatus.PROCESSING
            
            # Simuler l'exécution du trade (remplacé par l'appel réel à l'agent)
            trade_execution = None
            if strategy_signal and strategy_signal.get("action") != "HOLD":
                trade_execution = {
                    "trade_id": f"trade_{datetime.utcnow().timestamp()}",
                    "action": strategy_signal["action"],
                    "quantity": strategy_signal["position_size"],
                    "price": market_data["price"],
                    "status": "FILLED",
                    "timestamp": datetime.utcnow()
                }
            
            # Mettre à jour le statut
            self.agent_status[agent_name].status = AgentStatus.RUNNING
            self.agent_status[agent_name].last_execution = datetime.utcnow()
            self.agent_status[agent_name].execution_count += 1
            self.agent_status[agent_name].processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            logger.info("✅ Trader exécuté (sync)", trade=trade_execution)
            return trade_execution
            
        except Exception as e:
            self.agent_status[agent_name].status = AgentStatus.ERROR
            self.agent_status[agent_name].error_count += 1
            self.agent_status[agent_name].last_error = str(e)
            logger.error("❌ Erreur Trader (sync)", error=str(e))
            return None
    
    async def _execute_logger(self, market_data: Dict[str, Any], prediction: Optional[Dict[str, Any]], 
                             strategy_signal: Optional[Dict[str, Any]], trade_execution: Optional[Dict[str, Any]]):
        """Exécute l'agent Logger."""
        agent_name = "logger"
        start_time = datetime.utcnow()
        
        try:
            self.agent_status[agent_name].status = AgentStatus.PROCESSING
            
            # Simuler le logging (remplacé par l'appel réel à l'agent)
            log_entry = {
                "timestamp": datetime.utcnow(),
                "market_data": market_data,
                "prediction": prediction,
                "strategy_signal": strategy_signal,
                "trade_execution": trade_execution
            }
            
            # Mettre à jour le statut
            self.agent_status[agent_name].status = AgentStatus.RUNNING
            self.agent_status[agent_name].last_execution = datetime.utcnow()
            self.agent_status[agent_name].execution_count += 1
            self.agent_status[agent_name].processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            logger.info("✅ Logger exécuté", log_entry=log_entry)
            
        except Exception as e:
            self.agent_status[agent_name].status = AgentStatus.ERROR
            self.agent_status[agent_name].error_count += 1
            self.agent_status[agent_name].last_error = str(e)
            logger.error("❌ Erreur Logger", error=str(e))
    
    def _execute_logger_sync(self, market_data: Dict[str, Any], prediction: Optional[Dict[str, Any]], 
                            strategy_signal: Optional[Dict[str, Any]], trade_execution: Optional[Dict[str, Any]]):
        """Exécute l'agent Logger (version synchrone)."""
        agent_name = "logger"
        start_time = datetime.utcnow()
        
        try:
            self.agent_status[agent_name].status = AgentStatus.PROCESSING
            
            # Simuler le logging (remplacé par l'appel réel à l'agent)
            log_entry = {
                "timestamp": datetime.utcnow(),
                "market_data": market_data,
                "prediction": prediction,
                "strategy_signal": strategy_signal,
                "trade_execution": trade_execution
            }
            
            # Mettre à jour le statut
            self.agent_status[agent_name].status = AgentStatus.RUNNING
            self.agent_status[agent_name].last_execution = datetime.utcnow()
            self.agent_status[agent_name].execution_count += 1
            self.agent_status[agent_name].processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            logger.info("✅ Logger exécuté (sync)", log_entry=log_entry)
            
        except Exception as e:
            self.agent_status[agent_name].status = AgentStatus.ERROR
            self.agent_status[agent_name].error_count += 1
            self.agent_status[agent_name].last_error = str(e)
            logger.error("❌ Erreur Logger (sync)", error=str(e))
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Retourne le statut complet du pipeline."""
        # Convertir les agents en format sérialisable
        agents_dict = {}
        for name, status in self.agent_status.items():
            agent_dict = asdict(status)
            # Convertir l'enum AgentStatus en string
            agent_dict['status'] = status.status.value
            agents_dict[name] = agent_dict
        
        return {
            "is_running": self.is_running,
            "execution_interval": self.execution_interval,
            "agents": agents_dict,
            "pipeline_data_count": len(self.pipeline_data),
            "last_execution": max([status.last_execution for status in self.agent_status.values() if status.last_execution], default=None)
        }
    
    def get_pipeline_data(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retourne les dernières données du pipeline."""
        recent_data = self.pipeline_data[-limit:] if self.pipeline_data else []
        return [asdict(data) for data in recent_data]
    
    def get_agent_status(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Retourne le statut d'un agent spécifique."""
        if agent_name in self.agent_status:
            agent_dict = asdict(self.agent_status[agent_name])
            # Convertir l'enum AgentStatus en string
            agent_dict['status'] = self.agent_status[agent_name].status.value
            return agent_dict
        return None

# Instance globale du pipeline manager
pipeline_manager = PipelineManager()
