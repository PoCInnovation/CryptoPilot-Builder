"""Module de configuration centralisée pour le pipeline de trading."""

import os
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class PredictorConfig:
    """Configuration du modèle d'IA Predictor."""
    model_type: str = "LSTM_Simple"
    horizon: int = 5
    confidence_threshold: float = 0.6
    max_history: int = 100
    input_size: int = 10
    hidden_size: int = 32
    output_size: int = 1

@dataclass
class StrategyConfig:
    """Configuration de la stratégie de trading."""
    max_position_size: float = 0.1
    max_daily_loss: float = 0.05
    min_confidence: float = 0.7
    stop_loss: float = 0.02
    take_profit: float = 0.04
    max_open_trades: int = 3
    buy_threshold: float = 0.65
    sell_threshold: float = 0.35

@dataclass
class TraderConfig:
    """Configuration du trader."""
    paper_trading: bool = True
    max_slippage: float = 0.005
    min_order_size: float = 10
    max_order_size: float = 1000
    retry_attempts: int = 3
    retry_delay: int = 1
    initial_capital: float = 10000

@dataclass
class LoggerConfig:
    """Configuration du monitoring."""
    retention_days: int = 30
    alert_threshold_pnl: float = -100
    alert_threshold_winrate: float = 0.4
    performance_update_interval: int = 300
    max_alerts: int = 100
    drawdown_alert_threshold: float = 500

@dataclass
class DataCollectorConfig:
    """Configuration du collecteur de données."""
    interval: int = 60
    max_tokens: int = 10
    timeout: int = 30
    rate_limit: int = 100

@dataclass
class MLModelConfig:
    """Configuration des modèles ML."""
    use_real_lstm: bool = False
    lstm_model_path: str = "models/lstm_trading_model.h5"
    use_transformer: bool = False
    transformer_model_path: str = "models/transformer_trading_model.pt"
    use_asi_model: bool = False
    asi_model_path: str = "models/asi1_mini_model.pt"

@dataclass
class TechnicalIndicatorsConfig:
    """Configuration des indicateurs techniques."""
    use_moving_averages: bool = True
    ma_periods: List[int] = None
    use_rsi: bool = True
    rsi_period: int = 14
    use_macd: bool = True
    use_bollinger_bands: bool = True
    bollinger_period: int = 20
    bollinger_std: int = 2

@dataclass
class SecurityConfig:
    """Configuration de la sécurité."""
    enable_circuit_breaker: bool = True
    circuit_breaker_fail_max: int = 5
    circuit_breaker_timeout: int = 60
    enable_kill_switch: bool = True
    kill_switch_loss_threshold: float = -500

@dataclass
class NotificationConfig:
    """Configuration des notifications."""
    enable_email: bool = False
    notification_email: str = ""
    enable_discord: bool = False
    discord_webhook_url: str = ""
    enable_telegram: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""

class TradingConfig:
    """Configuration centralisée du pipeline de trading."""
    
    def __init__(self):
        self._load_config()
    
    def _load_config(self):
        """Charge la configuration depuis les variables d'environnement."""
        
        # Configuration de base
        self.paper_trading = os.getenv("PAPER_TRADING", "true").lower() == "true"
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Ports des agents
        self.data_collector_port = int(os.getenv("DATA_COLLECTOR_PORT", "9001"))
        self.predictor_port = int(os.getenv("PREDICTOR_PORT", "9002"))
        self.strategy_port = int(os.getenv("STRATEGY_PORT", "9003"))
        self.trader_port = int(os.getenv("TRADER_PORT", "9004"))
        self.logger_port = int(os.getenv("LOGGER_PORT", "9005"))
        
        # Configuration du Predictor
        self.predictor = PredictorConfig(
            model_type=os.getenv("PREDICTOR_MODEL_TYPE", "LSTM_Simple"),
            horizon=int(os.getenv("PREDICTOR_HORIZON", "5")),
            confidence_threshold=float(os.getenv("PREDICTOR_CONFIDENCE_THRESHOLD", "0.6")),
            max_history=int(os.getenv("PREDICTOR_MAX_HISTORY", "100")),
            input_size=int(os.getenv("PREDICTOR_INPUT_SIZE", "10")),
            hidden_size=int(os.getenv("PREDICTOR_HIDDEN_SIZE", "32")),
            output_size=int(os.getenv("PREDICTOR_OUTPUT_SIZE", "1"))
        )
        
        # Configuration de la Strategy
        self.strategy = StrategyConfig(
            max_position_size=float(os.getenv("STRATEGY_MAX_POSITION_SIZE", "0.1")),
            max_daily_loss=float(os.getenv("STRATEGY_MAX_DAILY_LOSS", "0.05")),
            min_confidence=float(os.getenv("STRATEGY_MIN_CONFIDENCE", "0.7")),
            stop_loss=float(os.getenv("STRATEGY_STOP_LOSS", "0.02")),
            take_profit=float(os.getenv("STRATEGY_TAKE_PROFIT", "0.04")),
            max_open_trades=int(os.getenv("STRATEGY_MAX_OPEN_TRADES", "3")),
            buy_threshold=float(os.getenv("STRATEGY_BUY_THRESHOLD", "0.65")),
            sell_threshold=float(os.getenv("STRATEGY_SELL_THRESHOLD", "0.35"))
        )
        
        # Configuration du Trader
        self.trader = TraderConfig(
            paper_trading=os.getenv("TRADER_PAPER_TRADING", "true").lower() == "true",
            max_slippage=float(os.getenv("TRADER_MAX_SLIPPAGE", "0.005")),
            min_order_size=float(os.getenv("TRADER_MIN_ORDER_SIZE", "10")),
            max_order_size=float(os.getenv("TRADER_MAX_ORDER_SIZE", "1000")),
            retry_attempts=int(os.getenv("TRADER_RETRY_ATTEMPTS", "3")),
            retry_delay=int(os.getenv("TRADER_RETRY_DELAY", "1")),
            initial_capital=float(os.getenv("TRADER_INITIAL_CAPITAL", "10000"))
        )
        
        # Configuration du Logger
        self.logger = LoggerConfig(
            retention_days=int(os.getenv("LOGGER_RETENTION_DAYS", "30")),
            alert_threshold_pnl=float(os.getenv("LOGGER_ALERT_THRESHOLD_PNL", "-100")),
            alert_threshold_winrate=float(os.getenv("LOGGER_ALERT_THRESHOLD_WINRATE", "0.4")),
            performance_update_interval=int(os.getenv("LOGGER_PERFORMANCE_UPDATE_INTERVAL", "300")),
            max_alerts=int(os.getenv("LOGGER_MAX_ALERTS", "100")),
            drawdown_alert_threshold=float(os.getenv("LOGGER_DRAWDOWN_ALERT_THRESHOLD", "500"))
        )
        
        # Configuration du DataCollector
        self.data_collector = DataCollectorConfig(
            interval=int(os.getenv("DATA_COLLECTOR_INTERVAL", "60")),
            max_tokens=int(os.getenv("DATA_COLLECTOR_MAX_TOKENS", "10")),
            timeout=int(os.getenv("DATA_COLLECTOR_TIMEOUT", "30")),
            rate_limit=int(os.getenv("DATA_COLLECTOR_RATE_LIMIT", "100"))
        )
        
        # Configuration des modèles ML
        self.ml_models = MLModelConfig(
            use_real_lstm=os.getenv("USE_REAL_LSTM_MODEL", "false").lower() == "true",
            lstm_model_path=os.getenv("LSTM_MODEL_PATH", "models/lstm_trading_model.h5"),
            use_transformer=os.getenv("USE_TRANSFORMER_MODEL", "false").lower() == "true",
            transformer_model_path=os.getenv("TRANSFORMER_MODEL_PATH", "models/transformer_trading_model.pt"),
            use_asi_model=os.getenv("USE_ASI_MODEL", "false").lower() == "true",
            asi_model_path=os.getenv("ASI_MODEL_PATH", "models/asi1_mini_model.pt")
        )
        
        # Configuration des indicateurs techniques
        ma_periods_str = os.getenv("MA_PERIODS", "5,10,20,50")
        ma_periods = [int(p) for p in ma_periods_str.split(",")]
        
        self.technical_indicators = TechnicalIndicatorsConfig(
            use_moving_averages=os.getenv("USE_MOVING_AVERAGES", "true").lower() == "true",
            ma_periods=ma_periods,
            use_rsi=os.getenv("USE_RSI", "true").lower() == "true",
            rsi_period=int(os.getenv("RSI_PERIOD", "14")),
            use_macd=os.getenv("USE_MACD", "true").lower() == "true",
            use_bollinger_bands=os.getenv("USE_BOLLINGER_BANDS", "true").lower() == "true",
            bollinger_period=int(os.getenv("BOLLINGER_PERIOD", "20")),
            bollinger_std=int(os.getenv("BOLLINGER_STD", "2"))
        )
        
        # Configuration de la sécurité
        self.security = SecurityConfig(
            enable_circuit_breaker=os.getenv("ENABLE_CIRCUIT_BREAKER", "true").lower() == "true",
            circuit_breaker_fail_max=int(os.getenv("CIRCUIT_BREAKER_FAIL_MAX", "5")),
            circuit_breaker_timeout=int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "60")),
            enable_kill_switch=os.getenv("ENABLE_KILL_SWITCH", "true").lower() == "true",
            kill_switch_loss_threshold=float(os.getenv("KILL_SWITCH_LOSS_THRESHOLD", "-500"))
        )
        
        # Configuration des notifications
        self.notifications = NotificationConfig(
            enable_email=os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true",
            notification_email=os.getenv("NOTIFICATION_EMAIL", ""),
            enable_discord=os.getenv("ENABLE_DISCORD_NOTIFICATIONS", "false").lower() == "true",
            discord_webhook_url=os.getenv("DISCORD_WEBHOOK_URL", ""),
            enable_telegram=os.getenv("ENABLE_TELEGRAM_NOTIFICATIONS", "false").lower() == "true",
            telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
            telegram_chat_id=os.getenv("TELEGRAM_CHAT_ID", "")
        )
        
        # Configuration des APIs
        self.token_price_api = os.getenv("TOKEN_PRICE_API", "simulation")
        self.coingecko_api_url = os.getenv("COINGECKO_API_URL", "https://api.coingecko.com/api/v3")
        self.coinpaprika_api_url = os.getenv("COINPAPRIKA_API_URL", "https://api.coinpaprika.com/v1")
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Retourne la configuration pour un agent spécifique."""
        configs = {
            "predictor": self.predictor,
            "strategy": self.strategy,
            "trader": self.trader,
            "logger": self.logger,
            "data_collector": self.data_collector
        }
        return configs.get(agent_name, {})
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertit la configuration en dictionnaire."""
        return {
            "ethereum_rpc_url": self.ethereum_rpc_url,
            "paper_trading": self.paper_trading,
            "log_level": self.log_level,
            "ports": {
                "data_collector": self.data_collector_port,
                "predictor": self.predictor_port,
                "strategy": self.strategy_port,
                "trader": self.trader_port,
                "logger": self.logger_port
            },
            "predictor": self.predictor.__dict__,
            "strategy": self.strategy.__dict__,
            "trader": self.trader.__dict__,
            "logger": self.logger.__dict__,
            "data_collector": self.data_collector.__dict__,
            "ml_models": self.ml_models.__dict__,
            "technical_indicators": self.technical_indicators.__dict__,
            "security": self.security.__dict__,
            "notifications": self.notifications.__dict__
        }

# Instance globale de configuration
config = TradingConfig()
