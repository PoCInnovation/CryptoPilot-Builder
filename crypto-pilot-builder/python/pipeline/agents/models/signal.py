"""Modèles pour les signaux de trading."""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SignalType(str, Enum):
    """Types de signaux de trading."""
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"


class Signal(BaseModel):
    """Signal de trading généré par la stratégie."""
    symbol: str = Field(..., description="Paire de trading")
    signal_type: SignalType = Field(..., description="Type de signal")
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Confiance du signal (0-1)"
    )
    price: float = Field(..., description="Prix actuel")
    position_size: float = Field(..., description="Taille de position recommandée")
    stop_loss: float = Field(..., description="Stop loss recommandé")
    take_profit: float = Field(..., description="Take profit recommandé")
    prediction_data: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Données de prédiction utilisées"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp du signal"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class TradeSignal(BaseModel):
    """Signal de trading généré par la stratégie."""
    symbol: str = Field(..., description="Paire de trading")
    action: Literal["BUY", "SELL", "HOLD"] = Field(..., description="Action recommandée")
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Confiance du signal (0-1)"
    )
    reason: str = Field(..., description="Raison du signal")
    predicted_price: Optional[float] = Field(
        default=None,
        description="Prix prédit"
    )
    stop_loss: Optional[float] = Field(
        default=None,
        description="Stop loss recommandé"
    )
    take_profit: Optional[float] = Field(
        default=None,
        description="Take profit recommandé"
    )
    position_size: Optional[float] = Field(
        default=None,
        description="Taille de position recommandée"
    )
    risk_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Score de risque (0-1)"
    )
    technical_indicators: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Indicateurs techniques utilisés"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp du signal"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
