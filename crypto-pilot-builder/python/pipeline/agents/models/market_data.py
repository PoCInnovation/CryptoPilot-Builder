"""Modèles pour les données de marché."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class OHLCV(BaseModel):
    """Données OHLCV (Open, High, Low, Close, Volume)."""
    timestamp: int = Field(..., description="Timestamp Unix en millisecondes")
    open: float = Field(..., description="Prix d'ouverture")
    high: float = Field(..., description="Prix le plus haut")
    low: float = Field(..., description="Prix le plus bas")
    close: float = Field(..., description="Prix de fermeture")
    volume: float = Field(..., description="Volume échangé")


class MarketData(BaseModel):
    """Données de marché complètes."""
    symbol: str = Field(..., description="Paire de trading (ex: BTCUSDT)")
    timeframe: str = Field(..., description="Timeframe (1m, 5m, 15m, 1h)")
    ohlcv: List[OHLCV] = Field(..., description="Données OHLCV")
    features: Optional[Dict[str, Any]] = Field(
        default=None, 
        description="Features techniques calculées (RSI, MACD, etc.)"
    )
    news_sentiment: Optional[float] = Field(
        default=None, 
        description="Sentiment des news (-1 à 1)"
    )
    social_sentiment: Optional[float] = Field(
        default=None, 
        description="Sentiment social (-1 à 1)"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de collecte"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
