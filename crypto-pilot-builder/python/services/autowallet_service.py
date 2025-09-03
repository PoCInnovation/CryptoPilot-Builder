#!/usr/bin/env python3
"""
Service principal pour l'AutoWallet
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from .news_service import news_service
from .ai_analyzer import ai_analyzer
from .alert_service import alert_service

logger = logging.getLogger(__name__)

@dataclass
class AutowalletConfig:
    """Configuration de l'AutoWallet"""
    user_id: str
    is_active: bool = True
    analysis_interval: int = 15  # minutes
    max_investment_per_trade: float = 100.0
    risk_tolerance: str = "medium"  # low, medium, high
    investment_strategy: str = "balanced"  # conservative, balanced, aggressive
    min_confidence_score: float = 0.3
    min_confidence_threshold: float = 0.3  # Alias pour compatibilité
    max_daily_trades: int = 10
    stop_loss_percentage: float = 5.0
    take_profit_percentage: float = 15.0
    auto_analysis: bool = True  # Analyse automatique des news
    crypto_whitelist: List[str] = None
    created_at: datetime = None
    updated_at: datetime = None

    def __post_init__(self):
        if self.crypto_whitelist is None:
            self.crypto_whitelist = ['BTC', 'ETH', 'ADA', 'DOT', 'SOL']
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
        
        # Gestion de la compatibilité des noms de champs
        if hasattr(self, 'min_confidence_threshold') and not hasattr(self, 'min_confidence_score'):
            self.min_confidence_score = self.min_confidence_threshold
        elif hasattr(self, 'min_confidence_score') and not hasattr(self, 'min_confidence_threshold'):
            self.min_confidence_threshold = self.min_confidence_score

@dataclass
class TradeHistory:
    """Historique des trades"""
    id: str
    user_id: str
    crypto_symbol: str
    action: str  # BUY, SELL, HOLD
    amount: float
    price: float
    confidence_score: float
    news_id: str
    reasoning: str
    status: str  # pending, executed, cancelled
    executed_at: datetime
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class AutowalletService:
    """Service principal pour l'AutoWallet"""
    
    def __init__(self):
        self.news_service = news_service
        self.ai_analyzer = ai_analyzer
        self.alert_service = alert_service
        
        # Stockage en mémoire (remplacer par base de données en production)
        self.configs: Dict[str, AutowalletConfig] = {}
        self.trade_history: Dict[str, List[TradeHistory]] = {}
        self.monitoring_threads: Dict[str, threading.Thread] = {}
        self.stop_monitoring: Dict[str, bool] = {}
        
        logger.info("Service AutoWallet initialisé")
    
    def create_autowallet(self, user_id: str, config_data: dict) -> str:
        """Crée une nouvelle configuration d'AutoWallet"""
        try:
            # Générer un ID unique
            autowallet_id = f"aw_{user_id}_{int(time.time())}"
            
            # Créer la configuration
            config = AutowalletConfig(
                user_id=user_id,
                **config_data
            )
            
            # Sauvegarder
            self.configs[autowallet_id] = config
            self.trade_history[user_id] = []
            
            logger.info(f"AutoWallet créé pour l'utilisateur {user_id}: {autowallet_id}")
            
            # Démarrer l'analyse automatique si activée
            if config.auto_analysis:
                self.start_auto_analysis(user_id)
            
            return autowallet_id
            
        except Exception as e:
            logger.error(f"Erreur lors de la création de l'AutoWallet: {e}")
            raise
    
    def get_autowallet_status(self, user_id: str) -> dict:
        """Récupère le statut de l'AutoWallet d'un utilisateur"""
        try:
            # Chercher la configuration
            config = None
            for aw_id, aw_config in self.configs.items():
                if aw_config.user_id == user_id:
                    config = aw_config
                    break
            
            if not config:
                return {"error": "Autowallet non trouvé"}
            
            # Calculer les statistiques
            user_trades = self.trade_history.get(user_id, [])
            today_trades = [
                trade for trade in user_trades 
                if trade.executed_at.date() == datetime.utcnow().date()
            ]
            
            # Vérifier si le monitoring est actif
            is_monitoring = user_id in self.monitoring_threads and not self.stop_monitoring.get(user_id, False)
            
            return {
                "is_active": config.is_active,
                "is_monitoring": is_monitoring,
                "analysis_interval": config.analysis_interval,
                "max_investment_per_trade": config.max_investment_per_trade,
                "risk_tolerance": config.risk_tolerance,
                "investment_strategy": config.investment_strategy,
                "min_confidence_score": config.min_confidence_score,
                "max_daily_trades": config.max_daily_trades,
                "stop_loss_percentage": config.stop_loss_percentage,
                "take_profit_percentage": config.take_profit_percentage,
                "auto_analysis": config.auto_analysis,
                "crypto_whitelist": config.crypto_whitelist,
                "today_trades": len(today_trades),
                "total_trades": len(user_trades),
                "created_at": config.created_at.isoformat(),
                "updated_at": config.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut: {e}")
            return {"error": str(e)}
    
    def update_autowallet_config(self, user_id: str, updates: dict) -> bool:
        """Met à jour la configuration de l'AutoWallet"""
        try:
            # Trouver la configuration
            config = None
            for aw_id, aw_config in self.configs.items():
                if aw_config.user_id == user_id:
                    config = aw_config
                    break
            
            if not config:
                return False
            
            # Mettre à jour les champs
            for key, value in updates.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            
            config.updated_at = datetime.utcnow()
            
            # Redémarrer l'analyse automatique si nécessaire
            if config.auto_analysis and user_id not in self.monitoring_threads:
                self.start_auto_analysis(user_id)
            elif not config.auto_analysis and user_id in self.monitoring_threads:
                self.stop_auto_analysis(user_id)
            
            logger.info(f"Configuration mise à jour pour l'utilisateur {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour: {e}")
            return False
    
    def start_auto_analysis(self, user_id: str) -> bool:
        """Démarre l'analyse automatique pour un utilisateur"""
        try:
            if user_id in self.monitoring_threads:
                logger.warning(f"Analyse automatique déjà active pour l'utilisateur {user_id}")
                return True
            
            # Trouver la configuration
            config = None
            for aw_id, aw_config in self.configs.items():
                if aw_config.user_id == user_id:
                    config = aw_config
                    break
            
            if not config:
                logger.error(f"Configuration non trouvée pour l'utilisateur {user_id}")
                return False
            
            # Arrêter le monitoring précédent si actif
            self.stop_monitoring[user_id] = False
            
            # Créer le thread de monitoring
            thread = threading.Thread(
                target=self._monitoring_loop,
                args=(user_id,),
                daemon=True
            )
            
            self.monitoring_threads[user_id] = thread
            thread.start()
            
            logger.info(f"Analyse automatique démarrée pour l'utilisateur {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du démarrage de l'analyse automatique: {e}")
            return False

    def start_monitoring(self, user_id: str) -> bool:
        """Alias pour start_auto_analysis (compatibilité)"""
        return self.start_auto_analysis(user_id)
    
    def stop_auto_analysis(self, user_id: str) -> bool:
        """Arrête l'analyse automatique pour un utilisateur"""
        try:
            if user_id not in self.monitoring_threads:
                return True
            
            # Signaler l'arrêt
            self.stop_monitoring[user_id] = True
            
            # Attendre la fin du thread
            thread = self.monitoring_threads[user_id]
            if thread.is_alive():
                thread.join(timeout=5)
            
            # Nettoyer
            del self.monitoring_threads[user_id]
            if user_id in self.stop_monitoring:
                del self.stop_monitoring[user_id]
            
            logger.info(f"Analyse automatique arrêtée pour l'utilisateur {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'arrêt de l'analyse automatique: {e}")
            return False
    
    def _monitoring_loop(self, user_id: str):
        """Boucle de monitoring automatique"""
        logger.info(f"Démarrage de la boucle de monitoring pour l'utilisateur {user_id}")
        
        while not self.stop_monitoring.get(user_id, False):
            try:
                # Récupérer la configuration
                config = None
                for aw_id, aw_config in self.configs.items():
                    if aw_config.user_id == user_id:
                        config = aw_config
                        break
                
                if not config or not config.is_active:
                    logger.info(f"AutoWallet inactif pour l'utilisateur {user_id}, arrêt du monitoring")
                    break
                
                # Vérifier la limite quotidienne de trades
                user_trades = self.trade_history.get(user_id, [])
                today_trades = [
                    trade for trade in user_trades 
                    if trade.executed_at.date() == datetime.utcnow().date()
                ]
                
                if len(today_trades) >= config.max_daily_trades:
                    logger.info(f"Limite quotidienne de trades atteinte pour l'utilisateur {user_id}")
                    time.sleep(config.analysis_interval * 60)
                    continue
                
                # Récupérer les news récentes
                recent_news = self.news_service.get_recent_news(hours=1)
                
                if recent_news:
                    logger.info(f"Analyse de {len(recent_news)} news pour l'utilisateur {user_id}")
                    
                    # Analyser les news
                    market_context = self.ai_analyzer.get_market_context()
                    alerts = self.ai_analyzer.analyze_news_for_investment(recent_news, market_context)
                    
                    # Filtrer les alertes selon la configuration
                    filtered_alerts = []
                    for alert in alerts:
                        if (alert.confidence_score >= config.min_confidence_score and
                            alert.crypto_symbol in config.crypto_whitelist):
                            filtered_alerts.append(alert)
                    
                    # Envoyer les alertes
                    if filtered_alerts:
                        logger.info(f"Envoi de {len(filtered_alerts)} alertes pour l'utilisateur {user_id}")
                        for alert in filtered_alerts:
                            self.alert_service.send_investment_alert(user_id, alert)
                            
                            # Créer un trade si c'est un BUY ou SELL
                            if alert.alert_type in ['BUY', 'SELL']:
                                self._create_trade_from_alert(user_id, alert, config)
                
                # Attendre l'intervalle suivant
                time.sleep(config.analysis_interval * 60)
                
            except Exception as e:
                logger.error(f"Erreur dans la boucle de monitoring pour l'utilisateur {user_id}: {e}")
                time.sleep(60)  # Attendre 1 minute en cas d'erreur
        
        logger.info(f"Arrêt de la boucle de monitoring pour l'utilisateur {user_id}")
    
    def _create_trade_from_alert(self, user_id: str, alert, config: AutowalletConfig):
        """Crée un trade à partir d'une alerte"""
        try:
            # Calculer le montant du trade
            trade_amount = min(config.max_investment_per_trade, 100.0)  # Montant par défaut
            
            # Créer le trade
            trade = TradeHistory(
                id=f"trade_{int(time.time())}",
                user_id=user_id,
                crypto_symbol=alert.crypto_symbol,
                action=alert.alert_type,
                amount=trade_amount,
                price=0.0,  # Prix à récupérer depuis une API de prix
                confidence_score=alert.confidence_score,
                news_id=alert.news_id,
                reasoning=alert.reasoning,
                status="pending",
                executed_at=datetime.utcnow()
            )
            
            # Ajouter à l'historique
            if user_id not in self.trade_history:
                self.trade_history[user_id] = []
            self.trade_history[user_id].append(trade)
            
            logger.info(f"Trade créé pour l'utilisateur {user_id}: {alert.alert_type} {alert.crypto_symbol}")
            
        except Exception as e:
            logger.error(f"Erreur lors de la création du trade: {e}")
    
    def get_trade_history(self, user_id: str, limit: int = 50) -> List[dict]:
        """Récupère l'historique des trades d'un utilisateur"""
        try:
            user_trades = self.trade_history.get(user_id, [])
            
            # Trier par date d'exécution (plus récent en premier)
            sorted_trades = sorted(user_trades, key=lambda x: x.executed_at, reverse=True)
            
            # Limiter le nombre de résultats
            limited_trades = sorted_trades[:limit]
            
            # Convertir en format JSON
            trades_data = []
            for trade in limited_trades:
                trades_data.append({
                    "id": trade.id,
                    "crypto_symbol": trade.crypto_symbol,
                    "action": trade.action,
                    "amount": trade.amount,
                    "price": trade.price,
                    "confidence_score": trade.confidence_score,
                    "news_id": trade.news_id,
                    "reasoning": trade.reasoning,
                    "status": trade.status,
                    "executed_at": trade.executed_at.isoformat(),
                    "created_at": trade.created_at.isoformat()
                })
            
            return trades_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'historique: {e}")
            return []
    
    def analyze_news_manually(self, user_id: str, news_ids: List[str]) -> List[dict]:
        """Analyse manuelle de news spécifiques"""
        try:
            # Récupérer la configuration
            config = None
            for aw_id, aw_config in self.configs.items():
                if aw_config.user_id == user_id:
                    config = aw_config
                    break
            
            if not config:
                return []
            
            # Récupérer les news spécifiées
            all_news = self.news_service.get_recent_news(hours=168)  # 1 semaine
            selected_news = [
                news for news in all_news 
                if news.id in news_ids
            ]
            
            if not selected_news:
                return []
            
            # Analyser les news
            market_context = self.ai_analyzer.get_market_context()
            alerts = self.ai_analyzer.analyze_news_for_investment(selected_news, market_context)
            
            # Filtrer selon la configuration
            filtered_alerts = []
            for alert in alerts:
                if (alert.confidence_score >= config.min_confidence_score and
                    alert.crypto_symbol in config.crypto_whitelist):
                    filtered_alerts.append(alert)
            
            # Convertir en format JSON
            alerts_data = []
            for alert in filtered_alerts:
                alerts_data.append({
                    "id": alert.id,
                    "news_id": alert.news_id,
                    "crypto_symbol": alert.crypto_symbol,
                    "alert_type": alert.alert_type,
                    "confidence_score": alert.confidence_score,
                    "reasoning": alert.reasoning,
                    "created_at": alert.created_at.isoformat(),
                    "priority": alert.priority
                })
            
            return alerts_data
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse manuelle: {e}")
            return []

    def get_user_alerts(self, user_id: str, limit: int = 20) -> List[dict]:
        """Récupère les alertes d'un utilisateur"""
        try:
            # Pour l'instant, on retourne les alertes récentes
            # En production, cela viendrait d'une base de données
            all_news = self.news_service.get_recent_news(hours=24)
            
            if not all_news:
                return []
            
            # Analyser les news récentes pour générer des alertes
            market_context = self.ai_analyzer.get_market_context()
            alerts = self.ai_analyzer.analyze_news_for_investment(all_news, market_context)
            
            # Limiter le nombre d'alertes
            limited_alerts = alerts[:limit]
            
            # Convertir en format JSON
            alerts_data = []
            for alert in limited_alerts:
                alerts_data.append({
                    "id": alert.id,
                    "news_id": alert.news_id,
                    "crypto_symbol": alert.crypto_symbol,
                    "alert_type": alert.alert_type,
                    "confidence_score": alert.confidence_score,
                    "reasoning": alert.reasoning,
                    "created_at": alert.created_at.isoformat(),
                    "priority": alert.priority
                })
            
            return alerts_data
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des alertes: {e}")
            return []

# Instance singleton
autowallet_service = AutowalletService()
