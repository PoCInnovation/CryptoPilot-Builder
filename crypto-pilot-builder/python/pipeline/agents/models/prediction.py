"""Modèles pour les prédictions ML."""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class Prediction(BaseModel):
    """Prédiction du modèle ML."""
    symbol: str = Field(..., description="Paire de trading")
    horizon: int = Field(..., description="Horizon de prédiction en minutes")
    direction_prob: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Probabilité de hausse (0-1)"
    )
    volatility: float = Field(
        ..., 
        ge=0.0,
        description="Volatilité prédite"
    )
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Confiance du modèle (0-1)"
    )
    model_name: str = Field(..., description="Nom du modèle utilisé")
    features_used: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Features utilisées pour la prédiction"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de la prédiction"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
