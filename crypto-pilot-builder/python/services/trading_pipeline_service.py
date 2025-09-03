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

from .news_service import news_service
from .ai_analyzer import ai_analyzer
from .alert_service import alert_service
from .autowallet_service import autowallet_service
from config.trading_pipeline_config import PIPELINE_CONFIG

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
        self.news_service = news_service
        self.ai_analyzer = ai_analyzer
        self.alert_service = alert_service
        self.autowallet_service = autowallet_service
        
        # Configuration de la pipeline
        self.pipeline_config = PIPELINE_CONFIG
        
        # État de la pipeline
        self.is_running = False
        self.pipeline_thread = None
        self.stop_pipeline = False
        
        # Cache des données
        self.market_data_cache: Dict[str, MarketData] = {}
        self.predictions_cache: Dict[str, TradingPrediction] = {}
        self.signals_cache: Dict[str, TradingSignal] = {}
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
            if self.is_running:
                logger.warning("Pipeline déjà en cours d'exécution")
                return True
            
            self.stop_pipeline = False
            self.is_running = True
            
            # Démarrer le thread principal de la pipeline
            self.pipeline_thread = threading.Thread(
                target=self._pipeline_main_loop,
                daemon=True
            )
            self.pipeline_thread.start()
            
            logger.info("Pipeline de trading démarrée avec succès")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de la pipeline: {e}")
            self.is_running = False
            return False
    
    def stop_pipeline(self) -> bool:
        """Arrête la pipeline de trading"""
        try:
            if not self.is_running:
                return True
            
            self.stop_pipeline = True
            self.is_running = False
            
            # Attendre la fin du thread
            if self.pipeline_thread and self.pipeline_thread.is_alive():
                self.pipeline_thread.join(timeout=10)
            
            logger.info("Pipeline de trading arrêtée")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt de la pipeline: {e}")
            return False
    
    def _pipeline_main_loop(self):
        """Boucle principale de la pipeline"""
        logger.info("Démarrage de la boucle principale de la pipeline")
        
        while not self.stop_pipeline and self.is_running:
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
        return {
            "is_running": self.is_running,
            "config": self.pipeline_config,
            "stats": self.stats,
            "market_data_count": len(self.market_data_cache),
            "predictions_count": len(self.predictions_cache),
            "signals_count": len(self.signals_cache),
            "trades_count": len(self.trades_cache)
        }
    
    def get_market_data(self, symbol: str = None) -> Dict[str, Any]:
        """Retourne les données de marché"""
        if symbol:
            data = self.market_data_cache.get(symbol)
            return data.__dict__ if data else None
        else:
            return {s: d.__dict__ for s, d in self.market_data_cache.items()}
    
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
