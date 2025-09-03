"""Modèles pour les ordres de trading."""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
from enum import Enum

from .signal import SignalType


class TradeStatus(str, Enum):
    """Statuts des trades."""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    FAILED = "failed"
    CLOSED = "closed"


class TradeType(str, Enum):
    """Types de trades."""
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"


class TradeRequest(BaseModel):
    """Requête de trade."""
    trade_id: str = Field(..., description="ID unique du trade")
    symbol: str = Field(..., description="Paire de trading")
    trade_type: TradeType = Field(..., description="Type de trade")
    side: SignalType = Field(..., description="Côté du trade (BUY/SELL)")
    quantity: float = Field(..., gt=0, description="Quantité à trader")
    price: float = Field(..., gt=0, description="Prix d'exécution")
    stop_loss: Optional[float] = Field(default=None, description="Stop loss")
    take_profit: Optional[float] = Field(default=None, description="Take profit")
    status: TradeStatus = Field(default=TradeStatus.PENDING, description="Statut du trade")
    realized_pnl: Optional[float] = Field(default=None, description="P&L réalisé")
    signal_data: Optional[Dict[str, Any]] = Field(default=None, description="Données du signal")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OrderRequest(BaseModel):
    """Demande d'ordre de trading."""
    symbol: str = Field(..., description="Paire de trading")
    side: Literal["buy", "sell"] = Field(..., description="Côté de l'ordre")
    size: float = Field(..., gt=0, description="Taille de l'ordre")
    order_type: Literal["market", "limit"] = Field(
        default="market",
        description="Type d'ordre"
    )
    price: Optional[float] = Field(
        default=None,
        description="Prix limite (pour les ordres limit)"
    )
    slippage_bps: int = Field(
        default=25,
        ge=0,
        le=1000,
        description="Slippage maximum en basis points"
    )
    max_gas_gwei: Optional[int] = Field(
        default=None,
        description="Gas maximum pour les ordres DEX"
    )
    idempotency_key: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Clé d'idempotence pour éviter les doubles"
    )
    exchange: Literal["binance", "uniswap", "pancakeswap"] = Field(
        default="binance",
        description="Exchange cible"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Métadonnées supplémentaires"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de la demande"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OrderResponse(BaseModel):
    """Réponse d'exécution d'ordre."""
    order_id: str = Field(..., description="ID de l'ordre")
    success: bool = Field(..., description="Succès de l'exécution")
    tx_hash: Optional[str] = Field(
        default=None,
        description="Hash de transaction (pour DEX)"
    )
    executed_price: Optional[float] = Field(
        default=None,
        description="Prix d'exécution"
    )
    executed_size: Optional[float] = Field(
        default=None,
        description="Taille exécutée"
    )
    fees: Optional[float] = Field(
        default=None,
        description="Frais de transaction"
    )
    slippage: Optional[float] = Field(
        default=None,
        description="Slippage réel"
    )
    error: Optional[str] = Field(
        default=None,
        description="Message d'erreur si échec"
    )
    status: Literal["pending", "filled", "cancelled", "failed"] = Field(
        default="pending",
        description="Statut de l'ordre"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp de la réponse"
    )

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
