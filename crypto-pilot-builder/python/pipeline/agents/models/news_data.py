"""Modèles pour les données de news et recommandations."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class NewsItem(BaseModel):
    """Article de news analysé."""
    id: str = Field(..., description="ID unique de la news")
    title: str = Field(..., description="Titre de la news")
    content: str = Field(..., description="Contenu de la news")
    source: str = Field(..., description="Source de la news")
    published_at: datetime = Field(..., description="Date de publication")
    url: str = Field(..., description="URL de la news")
    sentiment_score: float = Field(
        ..., 
        ge=-1.0, 
        le=1.0,
        description="Score de sentiment (-1 à 1)"
    )
    relevance_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Score de pertinence (0 à 1)"
    )
    crypto_mentions: List[str] = Field(
        default_factory=list,
        description="Cryptomonnaies mentionnées"
    )
    impact_level: str = Field(
        default="low",
        description="Niveau d'impact: low, medium, high, critical"
    )


class NewsRecommendation(BaseModel):
    """Recommandation basée sur l'analyse d'une news."""
    action: str = Field(..., description="Action recommandée: buy, sell, hold")
    confidence: float = Field(
        ..., 
        ge=0.0, 
        le=1.0,
        description="Confiance de la recommandation (0-1)"
    )
    reasoning: str = Field(..., description="Raisonnement de la recommandation")
    risk_level: str = Field(
        default="medium",
        description="Niveau de risque: low, medium, high"
    )
    time_horizon: str = Field(
        default="short_term",
        description="Horizon temporel: short_term, medium_term, long_term"
    )
    price_target: Optional[float] = Field(
        default=None,
        description="Cible de prix estimée"
    )
    news_id: str = Field(..., description="ID de la news analysée")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de la recommandation"
    )


class NewsData(BaseModel):
    """Données de news agrégées pour un symbole."""
    symbol: str = Field(..., description="Symbole de la cryptomonnaie")
    news_items: List[NewsItem] = Field(
        default_factory=list,
        description="Liste des news analysées"
    )
    recommendations: List[NewsRecommendation] = Field(
        default_factory=list,
        description="Recommandations générées"
    )
    aggregated_sentiment: float = Field(
        default=0.0,
        ge=-1.0,
        le=1.0,
        description="Sentiment agrégé des news (-1 à 1)"
    )
    aggregated_confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confiance agrégée des recommandations (0-1)"
    )
    dominant_action: str = Field(
        default="hold",
        description="Action dominante: buy, sell, hold"
    )
    news_count: int = Field(
        default=0,
        description="Nombre de news analysées"
    )
    high_impact_news_count: int = Field(
        default=0,
        description="Nombre de news à fort impact"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de collecte"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
