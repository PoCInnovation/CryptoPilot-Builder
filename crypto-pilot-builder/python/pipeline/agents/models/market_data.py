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


class NewsRecommendation(BaseModel):
    """Recommandation basée sur l'analyse des news."""
    action: str = Field(..., description="Action recommandée: buy, sell, hold")
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Confiance de la recommandation (0-1)"
    )
    reasoning: str = Field(..., description="Raisonnement de la recommandation")
    source: str = Field(..., description="Source de la news")
    news_id: str = Field(..., description="ID de la news analysée")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de la recommandation"
    )


class MarketData(BaseModel):
    """Données de marché complètes avec intégration des news."""
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
    # Nouvelles données de news intégrées
    news_recommendations: Optional[List[NewsRecommendation]] = Field(
        default=None,
        description="Recommandations basées sur l'analyse des news"
    )
    news_sentiment_aggregated: Optional[float] = Field(
        default=None,
        description="Sentiment agrégé des news (-1 à 1)"
    )
    news_confidence_aggregated: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confiance agrégée des recommandations news (0-1)"
    )
    news_count: Optional[int] = Field(
        default=0,
        description="Nombre de news analysées"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de collecte"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
