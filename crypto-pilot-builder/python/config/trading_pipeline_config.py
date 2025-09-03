#!/usr/bin/env python3
"""
Configuration pour la pipeline de trading unifiée
"""

import os
from typing import Dict, Any

# Configuration par défaut de la pipeline
DEFAULT_PIPELINE_CONFIG = {
    # Intervalles d'exécution (en secondes)
    "data_collection_interval": 60,      # Collecte des données toutes les minutes
    "prediction_interval": 300,          # Prédictions toutes les 5 minutes
    "signal_generation_interval": 300,   # Signaux toutes les 5 minutes
    "trade_execution_interval": 60,      # Exécution des trades toutes les minutes
    
    # Limites de trading
    "max_concurrent_trades": 5,          # Nombre maximum de trades simultanés
    "min_confidence_threshold": 0.7,     # Seuil de confiance minimum (70%)
    
    # Gestion des risques
    "risk_management": {
        "max_position_size": 0.1,        # 10% du capital maximum par position
        "max_daily_loss": 0.05,          # 5% de perte maximale par jour
        "stop_loss_percentage": 0.02,    # Stop loss à 2%
        "take_profit_percentage": 0.04,  # Take profit à 4%
        "max_drawdown": 0.15,            # Drawdown maximum de 15%
        "correlation_limit": 0.7,        # Limite de corrélation entre positions
    },
    
    # Configuration des données de marché
    "market_data": {
        "supported_symbols": ["BTC/USD", "ETH/USD", "ADA/USD", "DOT/USD", "SOL/USD"],
        "price_update_interval": 30,     # Mise à jour des prix toutes les 30 secondes
        "news_analysis_hours": 24,       # Analyser les news des dernières 24h
        "sentiment_weight": 0.6,         # Poids du sentiment des news dans l'analyse
        "technical_weight": 0.4,         # Poids des indicateurs techniques
    },
    
    # Configuration des modèles de prédiction
    "prediction_models": {
        "news_sentiment": {
            "enabled": True,
            "weight": 0.4,
            "min_news_count": 3,         # Nombre minimum de news pour une prédiction
        },
        "technical_indicators": {
            "enabled": True,
            "weight": 0.3,
            "indicators": ["RSI", "MACD", "BB", "MA"],
        },
        "market_momentum": {
            "enabled": True,
            "weight": 0.2,
            "lookback_periods": [1, 5, 15, 60],  # Minutes
        },
        "social_sentiment": {
            "enabled": False,             # Désactivé par défaut
            "weight": 0.1,
        }
    },
    
    # Configuration de l'exécution des trades
    "trade_execution": {
        "paper_trading": True,           # Mode simulation par défaut
        "max_slippage": 0.005,          # 0.5% de slippage maximum
        "min_order_size": 10,            # Taille minimale en USD
        "max_order_size": 1000,          # Taille maximale en USD
        "retry_attempts": 3,             # Nombre de tentatives
        "retry_delay": 1,                # Délai entre tentatives en secondes
    },
    
    # Configuration des alertes
    "alerts": {
        "enabled": True,
        "channels": ["email", "webhook"],  # Canaux d'alerte par défaut
        "min_priority": "medium",         # Priorité minimale pour les alertes
        "notification_cooldown": 300,     # Délai minimum entre notifications (5 min)
    },
    
    # Configuration du logging et monitoring
    "logging": {
        "level": "INFO",
        "file_logging": True,
        "log_file": "trading_pipeline.log",
        "max_log_size": "10MB",
        "backup_count": 5,
    },
    
    # Configuration des performances
    "performance": {
        "enable_metrics": True,
        "metrics_interval": 60,          # Collecte des métriques toutes les minutes
        "performance_history_days": 30,   # Historique des performances sur 30 jours
        "enable_profiling": False,       # Profiling désactivé par défaut
    }
}

def get_pipeline_config() -> Dict[str, Any]:
    """Récupère la configuration de la pipeline avec les variables d'environnement"""
    config = DEFAULT_PIPELINE_CONFIG.copy()
    
    # Variables d'environnement pour la configuration
    env_mappings = {
        "PIPELINE_DATA_COLLECTION_INTERVAL": ("data_collection_interval", int),
        "PIPELINE_PREDICTION_INTERVAL": ("prediction_interval", int),
        "PIPELINE_SIGNAL_INTERVAL": ("signal_generation_interval", int),
        "PIPELINE_TRADE_INTERVAL": ("trade_execution_interval", int),
        "PIPELINE_MAX_CONCURRENT_TRADES": ("max_concurrent_trades", int),
        "PIPELINE_MIN_CONFIDENCE": ("min_confidence_threshold", float),
        "PIPELINE_MAX_POSITION_SIZE": ("risk_management.max_position_size", float),
        "PIPELINE_MAX_DAILY_LOSS": ("risk_management.max_daily_loss", float),
        "PIPELINE_STOP_LOSS": ("risk_management.stop_loss_percentage", float),
        "PIPELINE_TAKE_PROFIT": ("risk_management.take_profit_percentage", float),
        "PIPELINE_PAPER_TRADING": ("trade_execution.paper_trading", lambda x: x.lower() == 'true'),
    }
    
    # Appliquer les variables d'environnement
    for env_var, (config_path, converter) in env_mappings.items():
        env_value = os.getenv(env_var)
        if env_value is not None:
            try:
                # Gérer les chemins imbriqués (ex: "risk_management.max_position_size")
                keys = config_path.split('.')
                current = config
                for key in keys[:-1]:
                    current = current[key]
                current[keys[-1]] = converter(env_value)
            except (KeyError, ValueError) as e:
                print(f"Erreur lors de la configuration de {env_var}: {e}")
    
    return config

def validate_config(config: Dict[str, Any]) -> bool:
    """Valide la configuration de la pipeline"""
    try:
        # Vérifications de base
        assert config["data_collection_interval"] > 0, "Intervalle de collecte doit être positif"
        assert config["prediction_interval"] > 0, "Intervalle de prédiction doit être positif"
        assert config["signal_generation_interval"] > 0, "Intervalle de génération de signaux doit être positif"
        assert config["trade_execution_interval"] > 0, "Intervalle d'exécution des trades doit être positif"
        
        # Vérifications des seuils
        assert 0 < config["min_confidence_threshold"] <= 1, "Seuil de confiance doit être entre 0 et 1"
        assert 0 < config["risk_management"]["max_position_size"] <= 1, "Taille de position max doit être entre 0 et 1"
        assert 0 < config["risk_management"]["max_daily_loss"] <= 1, "Perte quotidienne max doit être entre 0 et 1"
        
        # Vérifications des intervalles logiques
        assert config["data_collection_interval"] <= config["prediction_interval"], "Collecte doit être plus fréquente que les prédictions"
        assert config["prediction_interval"] <= config["signal_generation_interval"], "Prédictions doivent être plus fréquentes que les signaux"
        
        return True
        
    except AssertionError as e:
        print(f"Erreur de validation de la configuration: {e}")
        return False
    except Exception as e:
        print(f"Erreur lors de la validation: {e}")
        return False

# Configuration par défaut
PIPELINE_CONFIG = get_pipeline_config()

# Validation de la configuration
if not validate_config(PIPELINE_CONFIG):
    print("⚠️ Configuration invalide, utilisation de la configuration par défaut")
    PIPELINE_CONFIG = DEFAULT_PIPELINE_CONFIG
