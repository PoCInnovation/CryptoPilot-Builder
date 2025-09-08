#!/usr/bin/env python3
"""
Service unifié de pipeline de trading pour l'autowallet
Fusionne la pipeline d'agents (DataCollector, Predictor, Strategy, Trader) avec l'autowallet existant
"""

import asyncio
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json

# Import du vrai PipelineManager de la pipeline existante
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../pipeline'))
from pipeline.utils.pipeline_manager import pipeline_manager

logger = logging.getLogger(__name__)

@dataclass
class MarketData:
    """Données de marché unifiées"""
    symbol: str
    price: float
    volume: float
    timestamp: datetime
    news_sentiment: float = 0.0
    technical_indicators: Dict[str, Any] = None
    social_sentiment: float = 0.0

@dataclass
class TradingPrediction:
    """Prédiction de trading unifiée"""
    symbol: str
    direction_prob: float  # 0.0 = vente, 1.0 = achat
    confidence: float
    volatility: float
    reasoning: str
    timestamp: datetime
    model_name: str = "unified_model"

@dataclass
class TradingSignal:
    """Signal de trading unifié"""
    symbol: str
    signal_type: str  # BUY, SELL, HOLD
    confidence: float
    price: float
    position_size: float
    stop_loss: float
    take_profit: float
    reasoning: str
    timestamp: datetime

@dataclass
class TradeExecution:
    """Exécution de trade unifiée"""
    trade_id: str
    symbol: str
    signal_type: str
    quantity: float
    price: float
    status: str  # pending, executed, cancelled, failed
    pnl: Optional[float] = None
    timestamp: datetime = None

class TradingPipelineService:
    """Service unifié de pipeline de trading"""
    
    def __init__(self):
        # Utiliser le vrai PipelineManager de la pipeline existante
        self.pipeline_manager = pipeline_manager
        
        logger.info("TradingPipelineService initialisé avec le vrai PipelineManager")
        self.trades_cache: Dict[str, TradeExecution] = {}
        
        # Statistiques
        self.stats = {
            "total_signals": 0,
            "total_trades": 0,
            "successful_trades": 0,
            "total_pnl": 0.0,
            "last_update": None
        }
        
        logger.info("Service de pipeline de trading unifié initialisé")
    
    def start_pipeline(self) -> bool:
        """Démarre la pipeline de trading unifiée"""
        try:
            # Utiliser le vrai pipeline manager
            result = asyncio.run(self.pipeline_manager.start_pipeline())
            logger.info("Pipeline de trading démarrée via PipelineManager")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de la pipeline: {e}")
            return False
    
    def stop_pipeline(self) -> bool:
        """Arrête la pipeline de trading"""
        try:
            # Utiliser le vrai pipeline manager
            result = asyncio.run(self.pipeline_manager.stop_pipeline())
            logger.info("Pipeline de trading arrêtée via PipelineManager")
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt de la pipeline: {e}")
            return False
    
    def _pipeline_main_loop(self):
        """Boucle principale de la pipeline"""
        logger.info("Démarrage de la boucle principale de la pipeline")
        
        while not self.should_stop and self.is_running:
            try:
                # Étape 1: Collecte de données (DataCollector)
                self._collect_market_data()
                
                # Étape 2: Génération de prédictions (Predictor)
                self._generate_predictions()
                
                # Étape 3: Génération de signaux (Strategy)
                self._generate_trading_signals()
                
                # Étape 4: Exécution des trades (Trader)
                self._execute_trades()
                
                # Mise à jour des statistiques
                self._update_statistics()
                
                # Attendre l'intervalle suivant
                time.sleep(self.pipeline_config["data_collection_interval"])
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle principale de la pipeline: {e}")
                time.sleep(60)  # Attendre 1 minute en cas d'erreur
        
        logger.info("Arrêt de la boucle principale de la pipeline")
    
    def _collect_market_data(self):
        """Collecte les données de marché (remplace DataCollector)"""
        try:
            logger.debug("Collecte des données de marché...")
            
            # 1. Récupérer les news récentes (via le service existant)
            recent_news = self.news_service.get_recent_news(hours=1)
            
            # 2. Analyser le sentiment des news
            for news in recent_news:
                # Extraire les cryptomonnaies mentionnées
                if news.crypto_mentions:
                    for crypto in news.crypto_mentions:
                        symbol = f"{crypto}/USD"
                        
                        # Créer ou mettre à jour les données de marché
                        if symbol not in self.market_data_cache:
                            self.market_data_cache[symbol] = MarketData(
                                symbol=symbol,
                                price=0.0,  # À récupérer via API de prix
                                volume=0.0,
                                timestamp=datetime.utcnow(),
                                news_sentiment=news.sentiment_score,
                                technical_indicators={},
                                social_sentiment=0.0
                            )
                        else:
                            # Mettre à jour le sentiment des news
                            current_data = self.market_data_cache[symbol]
                            # Moyenne pondérée du sentiment
                            current_data.news_sentiment = (
                                current_data.news_sentiment * 0.7 + 
                                news.sentiment_score * 0.3
                            )
                            current_data.timestamp = datetime.utcnow()
            
            # 3. Récupérer les prix en temps réel (à implémenter)
            self._update_real_time_prices()
            
            logger.debug(f"Données de marché collectées pour {len(self.market_data_cache)} symboles")
            
        except Exception as e:
            logger.error(f"Erreur lors de la collecte des données de marché: {e}")
    
    def _update_real_time_prices(self):
        """Met à jour les prix en temps réel (remplace la collecte de prix du DataCollector)"""
        try:
            # TODO: Implémenter la récupération des prix via API (CoinGecko, Binance, etc.)
            # Pour l'instant, on utilise des prix simulés
            
            for symbol in self.market_data_cache:
                # Simulation de prix (à remplacer par vraie API)
                import random
                base_price = 50000 if "BTC" in symbol else 3000 if "ETH" in symbol else 100
                price_change = random.uniform(-0.02, 0.02)  # ±2%
                new_price = base_price * (1 + price_change)
                
                self.market_data_cache[symbol].price = new_price
                self.market_data_cache[symbol].volume = random.uniform(1000000, 10000000)
                
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des prix: {e}")
    
    def _generate_predictions(self):
        """Génère les prédictions de trading (remplace Predictor)"""
        try:
            logger.debug("Génération des prédictions...")
            
            for symbol, market_data in self.market_data_cache.items():
                # Utiliser l'analyseur IA existant pour générer des prédictions
                prediction = self._generate_prediction_for_symbol(symbol, market_data)
                
                if prediction:
                    self.predictions_cache[symbol] = prediction
            
            logger.debug(f"Prédictions générées pour {len(self.predictions_cache)} symboles")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des prédictions: {e}")
    
    def _generate_prediction_for_symbol(self, symbol: str, market_data: MarketData) -> Optional[TradingPrediction]:
        """Génère une prédiction pour un symbole spécifique"""
        try:
            # Utiliser l'analyseur IA existant
            # Analyser le sentiment des news
            news_sentiment = market_data.news_sentiment
            
            # Calculer la probabilité de direction basée sur le sentiment
            if news_sentiment > 0.3:
                direction_prob = 0.6 + (news_sentiment * 0.3)  # Tendance haussière
            elif news_sentiment < -0.3:
                direction_prob = 0.4 + (news_sentiment * 0.3)  # Tendance baissière
            else:
                direction_prob = 0.5  # Neutre
            
            # Normaliser entre 0 et 1
            direction_prob = max(0.0, min(1.0, direction_prob))
            
            # Calculer la confiance basée sur la force du sentiment
            confidence = min(0.9, abs(news_sentiment) + 0.5)
            
            # Calculer la volatilité (simulation)
            volatility = 0.02 + abs(news_sentiment) * 0.03
            
            # Générer le raisonnement
            if news_sentiment > 0.3:
                reasoning = f"Sentiment positif des news ({news_sentiment:.2f}) suggère une tendance haussière"
            elif news_sentiment < -0.3:
                reasoning = f"Sentiment négatif des news ({news_sentiment:.2f}) suggère une tendance baissière"
            else:
                reasoning = f"Sentiment neutre des news ({news_sentiment:.2f}), marché stable"
            
            return TradingPrediction(
                symbol=symbol,
                direction_prob=direction_prob,
                confidence=confidence,
                volatility=volatility,
                reasoning=reasoning,
                timestamp=datetime.utcnow(),
                model_name="unified_news_sentiment_model"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération de prédiction pour {symbol}: {e}")
            return None
    
    def _generate_trading_signals(self):
        """Génère les signaux de trading (remplace Strategy)"""
        try:
            logger.debug("Génération des signaux de trading...")
            
            for symbol, prediction in self.predictions_cache.items():
                # Vérifier la confiance minimale
                if prediction.confidence < self.pipeline_config["min_confidence_threshold"]:
                    continue
                
                # Générer le signal
                signal = self._generate_signal_from_prediction(prediction)
                
                if signal:
                    self.signals_cache[symbol] = signal
            
            logger.debug(f"Signaux générés pour {len(self.signals_cache)} symboles")
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération des signaux: {e}")
    
    def _generate_signal_from_prediction(self, prediction: TradingPrediction) -> Optional[TradingSignal]:
        """Génère un signal de trading à partir d'une prédiction"""
        try:
            # Déterminer le type de signal
            if prediction.direction_prob > 0.65:
                signal_type = "BUY"
            elif prediction.direction_prob < 0.35:
                signal_type = "SELL"
            else:
                signal_type = "HOLD"
            
            # Si c'est HOLD, pas de signal
            if signal_type == "HOLD":
                return None
            
            # Récupérer le prix actuel
            market_data = self.market_data_cache.get(prediction.symbol)
            if not market_data:
                return None
            
            current_price = market_data.price
            
            # Calculer la taille de position
            position_size = self._calculate_position_size(prediction)
            
            # Calculer stop loss et take profit
            if signal_type == "BUY":
                stop_loss = current_price * (1 - self.pipeline_config["risk_management"]["stop_loss_percentage"])
                take_profit = current_price * (1 + self.pipeline_config["risk_management"]["take_profit_percentage"])
            else:  # SELL
                stop_loss = current_price * (1 + self.pipeline_config["risk_management"]["stop_loss_percentage"])
                take_profit = current_price * (1 - self.pipeline_config["risk_management"]["take_profit_percentage"])
            
            return TradingSignal(
                symbol=prediction.symbol,
                signal_type=signal_type,
                confidence=prediction.confidence,
                price=current_price,
                position_size=position_size,
                stop_loss=stop_loss,
                take_profit=take_profit,
                reasoning=prediction.reasoning,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du signal: {e}")
            return None
    
    def _calculate_position_size(self, prediction: TradingPrediction) -> float:
        """Calcule la taille de position basée sur la confiance et le risque"""
        try:
            # Taille de base
            base_size = self.pipeline_config["risk_management"]["max_position_size"]
            
            # Ajustement basé sur la confiance
            confidence_factor = prediction.confidence
            
            # Ajustement basé sur la volatilité (plus de volatilité = position plus petite)
            volatility_factor = max(0.3, 1.0 - prediction.volatility * 10)
            
            # Calcul de la taille finale
            position_size = base_size * confidence_factor * volatility_factor
            
            # Limitation à la taille maximale
            position_size = min(position_size, self.pipeline_config["risk_management"]["max_position_size"])
            
            return round(position_size, 4)
            
        except Exception as e:
            logger.error(f"Erreur lors du calcul de la taille de position: {e}")
            return 0.01  # Taille minimale par défaut
    
    def _execute_trades(self):
        """Exécute les trades (remplace Trader)"""
        try:
            logger.debug("Exécution des trades...")
            
            # Vérifier le nombre maximum de trades concurrents
            if len(self.trades_cache) >= self.pipeline_config["max_concurrent_trades"]:
                logger.debug("Nombre maximum de trades concurrents atteint")
                return
            
            for symbol, signal in self.signals_cache.items():
                # Vérifier si on a déjà un trade ouvert sur ce symbole
                if symbol in self.trades_cache:
                    continue
                
                # Vérifier si le signal est récent (moins de 5 minutes)
                if (datetime.utcnow() - signal.timestamp).total_seconds() > 300:
                    continue
                
                # Exécuter le trade
                trade = self._execute_single_trade(signal)
                
                if trade:
                    self.trades_cache[symbol] = trade
                    
                    # Créer une alerte pour l'utilisateur
                    self._create_trading_alert(signal, trade)
            
            logger.debug(f"Trades exécutés: {len(self.trades_cache)} actifs")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution des trades: {e}")
    
    def _execute_single_trade(self, signal: TradingSignal) -> Optional[TradeExecution]:
        """Exécute un trade individuel"""
        try:
            # Générer un ID de trade unique
            trade_id = f"trade_{int(time.time())}_{signal.symbol}"
            
            # Simulation de l'exécution (à remplacer par vraie API de trading)
            execution_price = signal.price
            
            # Créer le trade
            trade = TradeExecution(
                trade_id=trade_id,
                symbol=signal.symbol,
                signal_type=signal.signal_type,
                quantity=signal.position_size,
                price=execution_price,
                status="executed",
                timestamp=datetime.utcnow()
            )
            
            logger.info(f"Trade exécuté: {signal.signal_type} {signal.symbol} à {execution_price}")
            
            return trade
            
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution du trade: {e}")
            return None
    
    def _create_trading_alert(self, signal: TradingSignal, trade: TradeExecution):
        """Crée une alerte de trading pour l'utilisateur"""
        try:
            # Créer une alerte d'investissement
            alert_data = {
                "crypto_symbol": signal.symbol.split('/')[0],  # Extraire BTC de BTC/USD
                "alert_type": signal.signal_type.lower(),
                "confidence_score": signal.confidence,
                "reasoning": f"Signal de trading généré automatiquement: {signal.reasoning}",
                "priority": "high" if signal.confidence > 0.8 else "medium"
            }
            
            # Envoyer l'alerte via le service existant
            # TODO: Intégrer avec le système d'alertes existant
            
            logger.info(f"Alerte de trading créée pour {signal.symbol}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'alerte: {e}")
    
    def _update_statistics(self):
        """Met à jour les statistiques de la pipeline"""
        try:
            self.stats["total_signals"] = len(self.signals_cache)
            self.stats["total_trades"] = len(self.trades_cache)
            self.stats["successful_trades"] = len([t for t in self.trades_cache.values() if t.status == "executed"])
            self.stats["last_update"] = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des statistiques: {e}")
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Retourne le statut de la pipeline"""
        # Utiliser le vrai pipeline manager
        status = self.pipeline_manager.get_pipeline_status()
        
        # Adapter le format pour l'API
        return {
            "is_running": status.get("is_running", False),
            "config": {
                "execution_interval": status.get("execution_interval", 60),
                "pipeline_version": "1.0.0"
            },
            "stats": {
                "total_trades": 0,
                "successful_trades": 0,
                "total_pnl": 0.0,
                "total_signals": 0,
                "last_update": status.get("last_execution")
            },
            "agents": status.get("agents", {}),  # Inclure les données des agents
            "last_execution": status.get("last_execution"),
            "market_data_count": 0,  # Sera mis à jour par les agents
            "predictions_count": 0,  # Sera mis à jour par les agents
            "signals_count": 0,      # Sera mis à jour par les agents
            "trades_count": 0        # Sera mis à jour par les agents
        }
    
    def get_market_data(self, symbol: str = None) -> Dict[str, Any]:
        """Retourne les données de marché avec prédictions et signaux"""
        # Utiliser les vraies données du pipeline manager
        pipeline_data = self.pipeline_manager.get_pipeline_data(limit=10)
        
        # Extraire toutes les données des dernières exécutions
        market_data = []
        for data in pipeline_data:
            if data.get("symbol") and data.get("price"):
                market_data.append({
                    "symbol": data["symbol"],
                    "price": data["price"],
                    "volume": data.get("volume", 0),
                    "timestamp": data["timestamp"],
                    "prediction": data.get("prediction"),
                    "strategy_signal": data.get("strategy_signal"),
                    "trade_execution": data.get("trade_execution")
                })
        
        return market_data
    
    def call_logger_agent(self) -> Dict[str, Any]:
        """Appelle le Logger Agent pour générer un rapport complet"""
        try:
            # Utiliser le pipeline manager pour appeler le logger agent
            pipeline_data = self.pipeline_manager.get_pipeline_data(limit=50)
            pipeline_status = self.pipeline_manager.get_pipeline_status()
            
            # Analyser les données pour extraire les informations importantes
            total_executions = len(pipeline_data)
            successful_executions = len([d for d in pipeline_data if d.get("prediction")])
            failed_executions = total_executions - successful_executions
            
            # Analyser les signaux de trading
            buy_signals = len([d for d in pipeline_data if d.get("strategy_signal", {}).get("action") == "BUY"])
            sell_signals = len([d for d in pipeline_data if d.get("strategy_signal", {}).get("action") == "SELL"])
            hold_signals = len([d for d in pipeline_data if d.get("strategy_signal", {}).get("action") == "HOLD"])
            
            # Analyser les prédictions
            up_predictions = len([d for d in pipeline_data if d.get("prediction", {}).get("direction") == "UP"])
            down_predictions = len([d for d in pipeline_data if d.get("prediction", {}).get("direction") == "DOWN"])
            
            # Analyser les trades
            filled_trades = len([d for d in pipeline_data if d.get("trade_execution", {}).get("status") == "FILLED"])
            pending_trades = len([d for d in pipeline_data if d.get("trade_execution", {}).get("status") == "PENDING"])
            
            # Générer une recommandation de trading
            recommendation = self._generate_trading_recommendation(pipeline_data)
            
            # Simuler l'appel au logger agent avec des données détaillées
            logger_result = {
                "agent_name": "logger",
                "timestamp": datetime.utcnow().isoformat(),
                "action": "generate_report",
                "pipeline_data_count": len(pipeline_data),
                "report": {
                    "summary": {
                        "total_executions": total_executions,
                        "successful_executions": successful_executions,
                        "failed_executions": failed_executions,
                        "last_execution": pipeline_data[-1]["timestamp"] if pipeline_data else None,
                        "pipeline_running": pipeline_status.get("is_running", True),
                        "recommendation": recommendation
                    },
                    "agents_info": pipeline_status.get("agents", {
                        "data_collector": "running",
                        "predictor": "running", 
                        "strategy": "running",
                        "trader": "running",
                        "logger": "running"
                    }),
                    "trading_analysis": {
                        "signals": {
                            "buy_signals": buy_signals,
                            "sell_signals": sell_signals,
                            "hold_signals": hold_signals,
                            "total_signals": buy_signals + sell_signals + hold_signals
                        },
                        "predictions": {
                            "up_predictions": up_predictions,
                            "down_predictions": down_predictions,
                            "total_predictions": up_predictions + down_predictions
                        },
                        "trades": {
                            "filled_trades": filled_trades,
                            "pending_trades": pending_trades,
                            "total_trades": filled_trades + pending_trades
                        }
                    },
                    "recent_activities": [
                        {
                            "timestamp": data.get("timestamp"),
                            "symbol": data.get("symbol"),
                            "price": data.get("price"),
                            "has_prediction": bool(data.get("prediction")),
                            "has_signal": bool(data.get("strategy_signal")),
                            "has_trade": bool(data.get("trade_execution")),
                            "prediction": data.get("prediction"),
                            "strategy_signal": data.get("strategy_signal"),
                            "trade_execution": data.get("trade_execution")
                        } for data in pipeline_data[-5:]
                    ],
                    "pipeline_info": {
                        "execution_interval": pipeline_status.get("execution_interval", 60),
                        "pipeline_data_count": len(pipeline_data),
                        "last_execution": pipeline_data[-1]["timestamp"] if pipeline_data else None
                    }
                },
                "status": "success"
            }
            
            logger.info("Logger Agent appelé avec succès")
            return logger_result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'appel au Logger Agent: {e}")
            return {
                "agent_name": "logger",
                "timestamp": datetime.utcnow().isoformat(),
                "action": "generate_report",
                "status": "error",
                "error": str(e)
            }
    
    def _generate_trading_recommendation(self, pipeline_data: List[Dict]) -> Dict[str, Any]:
        """Génère une recommandation de trading basée sur les données du pipeline"""
        if not pipeline_data:
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reason": "Aucune donnée disponible",
                "risk_level": "UNKNOWN"
            }
        
        # Analyser les dernières données
        recent_data = pipeline_data[-5:] if len(pipeline_data) >= 5 else pipeline_data
        
        # Compter les signaux
        buy_count = sum(1 for d in recent_data if d.get("strategy_signal", {}).get("action") == "BUY")
        sell_count = sum(1 for d in recent_data if d.get("strategy_signal", {}).get("action") == "SELL")
        hold_count = sum(1 for d in recent_data if d.get("strategy_signal", {}).get("action") == "HOLD")
        
        # Analyser les prédictions
        up_count = sum(1 for d in recent_data if d.get("prediction", {}).get("direction") == "UP")
        down_count = sum(1 for d in recent_data if d.get("prediction", {}).get("direction") == "DOWN")
        
        # Calculer la confiance
        total_signals = buy_count + sell_count + hold_count
        confidence = 0.0
        action = "HOLD"
        reason = "Données insuffisantes"
        risk_level = "MEDIUM"
        
        if total_signals > 0:
            if buy_count > sell_count and buy_count > hold_count:
                action = "BUY"
                confidence = buy_count / total_signals
                reason = f"Tendance haussière détectée ({buy_count}/{total_signals} signaux d'achat)"
                risk_level = "LOW" if confidence > 0.7 else "MEDIUM"
            elif sell_count > buy_count and sell_count > hold_count:
                action = "SELL"
                confidence = sell_count / total_signals
                reason = f"Tendance baissière détectée ({sell_count}/{total_signals} signaux de vente)"
                risk_level = "LOW" if confidence > 0.7 else "MEDIUM"
            else:
                action = "HOLD"
                confidence = hold_count / total_signals
                reason = f"Marché neutre ({hold_count}/{total_signals} signaux de maintien)"
                risk_level = "LOW"
        
        # Ajuster selon les prédictions
        if up_count > down_count and action == "BUY":
            confidence = min(confidence + 0.1, 1.0)
            reason += f" + Prédictions haussières ({up_count}/{up_count + down_count})"
        elif down_count > up_count and action == "SELL":
            confidence = min(confidence + 0.1, 1.0)
            reason += f" + Prédictions baissières ({down_count}/{up_count + down_count})"
        
        return {
            "action": action,
            "confidence": round(confidence, 2),
            "reason": reason,
            "risk_level": risk_level,
            "market_sentiment": "BULLISH" if up_count > down_count else "BEARISH" if down_count > up_count else "NEUTRAL"
        }
    
    def get_predictions(self, symbol: str = None) -> Dict[str, Any]:
        """Retourne les prédictions"""
        if symbol:
            pred = self.predictions_cache.get(symbol)
            return pred.__dict__ if pred else None
        else:
            return {s: p.__dict__ for s, p in self.predictions_cache.items()}
    
    def get_signals(self, symbol: str = None) -> Dict[str, Any]:
        """Retourne les signaux de trading"""
        if symbol:
            signal = self.signals_cache.get(symbol)
            return signal.__dict__ if signal else None
        else:
            return {s: sig.__dict__ for s, sig in self.signals_cache.items()}
    
    def get_trades(self, symbol: str = None) -> Dict[str, Any]:
        """Retourne les trades"""
        if symbol:
            trade = self.trades_cache.get(symbol)
            return trade.__dict__ if trade else None
        else:
            return {s: t.__dict__ for s, t in self.trades_cache.items()}

# Instance singleton
trading_pipeline_service = TradingPipelineService()
