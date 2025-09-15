"""Module pour le calcul des indicateurs techniques."""

import numpy as np
from typing import List, Dict, Any, Optional
import structlog

logger = structlog.get_logger(__name__)

class TechnicalIndicators:
    """Classe pour calculer les indicateurs techniques."""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> float:
        """Calcule le RSI (Relative Strength Index)."""
        if len(prices) < period + 1:
            return 50.0  # Valeur neutre par défaut
        
        # Calculer les gains et pertes
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        # Moyennes mobiles des gains et pertes
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return float(rsi)
    
    @staticmethod
    def calculate_moving_averages(prices: List[float], periods: List[int] = [5, 10, 20, 50]) -> Dict[str, float]:
        """Calcule les moyennes mobiles pour différentes périodes."""
        result = {}
        
        for period in periods:
            if len(prices) >= period:
                ma = np.mean(prices[-period:])
                result[f"ma_{period}"] = float(ma)
            else:
                result[f"ma_{period}"] = float(np.mean(prices)) if prices else 0.0
        
        return result
    
    @staticmethod
    def calculate_macd(prices: List[float], fast_period: int = 12, slow_period: int = 26, signal_period: int = 9) -> Dict[str, float]:
        """Calcule le MACD (Moving Average Convergence Divergence)."""
        if len(prices) < slow_period:
            return {
                "macd": 0.0,
                "macd_signal": 0.0,
                "macd_histogram": 0.0
            }
        
        # Moyennes mobiles exponentielles
        ema_fast = TechnicalIndicators._calculate_ema(prices, fast_period)
        ema_slow = TechnicalIndicators._calculate_ema(prices, slow_period)
        
        # MACD line
        macd_line = ema_fast - ema_slow
        
        # Signal line (EMA du MACD)
        macd_values = []
        for i in range(len(prices)):
            if i >= slow_period - 1:
                ema_fast_i = TechnicalIndicators._calculate_ema(prices[:i+1], fast_period)
                ema_slow_i = TechnicalIndicators._calculate_ema(prices[:i+1], slow_period)
                macd_values.append(ema_fast_i - ema_slow_i)
        
        if len(macd_values) >= signal_period:
            signal_line = TechnicalIndicators._calculate_ema(macd_values, signal_period)
        else:
            signal_line = macd_line
        
        # Histogram
        histogram = macd_line - signal_line
        
        return {
            "macd": float(macd_line),
            "macd_signal": float(signal_line),
            "macd_histogram": float(histogram)
        }
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict[str, float]:
        """Calcule les bandes de Bollinger."""
        if len(prices) < period:
            return {
                "bb_upper": 0.0,
                "bb_middle": 0.0,
                "bb_lower": 0.0,
                "bb_width": 0.0
            }
        
        # Moyenne mobile
        middle = np.mean(prices[-period:])
        
        # Écart-type
        std = np.std(prices[-period:])
        
        # Bandes
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        
        # Largeur des bandes
        width = (upper - lower) / middle if middle > 0 else 0
        
        return {
            "bb_upper": float(upper),
            "bb_middle": float(middle),
            "bb_lower": float(lower),
            "bb_width": float(width)
        }
    
    @staticmethod
    def calculate_stochastic(prices: List[float], period: int = 14) -> Dict[str, float]:
        """Calcule l'oscillateur stochastique."""
        if len(prices) < period:
            return {
                "stoch_k": 50.0,
                "stoch_d": 50.0
            }
        
        # Plus haut et plus bas sur la période
        high = max(prices[-period:])
        low = min(prices[-period:])
        current = prices[-1]
        
        if high == low:
            k_percent = 50.0
        else:
            k_percent = ((current - low) / (high - low)) * 100
        
        # %D (moyenne mobile de %K)
        k_values = []
        for i in range(period, len(prices)):
            period_high = max(prices[i-period:i])
            period_low = min(prices[i-period:i])
            period_current = prices[i-1]
            
            if period_high == period_low:
                k_values.append(50.0)
            else:
                k_values.append(((period_current - period_low) / (period_high - period_low)) * 100)
        
        d_percent = np.mean(k_values) if k_values else k_percent
        
        return {
            "stoch_k": float(k_percent),
            "stoch_d": float(d_percent)
        }
    
    @staticmethod
    def calculate_volume_indicators(prices: List[float], volumes: List[float]) -> Dict[str, float]:
        """Calcule les indicateurs basés sur le volume."""
        if len(prices) < 2 or len(volumes) < 2:
            return {
                "volume_sma": 0.0,
                "volume_ratio": 1.0,
                "price_volume_trend": 0.0
            }
        
        # Volume moyen
        volume_sma = np.mean(volumes[-20:]) if len(volumes) >= 20 else np.mean(volumes)
        
        # Ratio volume actuel / volume moyen
        current_volume = volumes[-1]
        volume_ratio = current_volume / volume_sma if volume_sma > 0 else 1.0
        
        # Price Volume Trend (PVT)
        pvt = 0.0
        for i in range(1, len(prices)):
            price_change = (prices[i] - prices[i-1]) / prices[i-1] if prices[i-1] > 0 else 0
            pvt += price_change * volumes[i]
        
        return {
            "volume_sma": float(volume_sma),
            "volume_ratio": float(volume_ratio),
            "price_volume_trend": float(pvt)
        }
    
    @staticmethod
    def calculate_all_indicators(prices: List[float], volumes: Optional[List[float]] = None) -> Dict[str, float]:
        """Calcule tous les indicateurs techniques."""
        if not prices:
            return {}
        
        indicators = {}
        
        # RSI
        indicators["rsi"] = TechnicalIndicators.calculate_rsi(prices)
        
        # Moyennes mobiles
        ma_indicators = TechnicalIndicators.calculate_moving_averages(prices)
        indicators.update(ma_indicators)
        
        # MACD
        macd_indicators = TechnicalIndicators.calculate_macd(prices)
        indicators.update(macd_indicators)
        
        # Bandes de Bollinger
        bb_indicators = TechnicalIndicators.calculate_bollinger_bands(prices)
        indicators.update(bb_indicators)
        
        # Stochastique
        stoch_indicators = TechnicalIndicators.calculate_stochastic(prices)
        indicators.update(stoch_indicators)
        
        # Volume (si disponible)
        if volumes and len(volumes) > 0:
            volume_indicators = TechnicalIndicators.calculate_volume_indicators(prices, volumes)
            indicators.update(volume_indicators)
        
        # Indicateurs supplémentaires
        if len(prices) >= 2:
            # Momentum
            indicators["momentum"] = float((prices[-1] - prices[-2]) / prices[-2] * 100)
            
            # Volatilité
            returns = []
            for i in range(1, len(prices)):
                if prices[i-1] > 0:
                    returns.append((prices[i] - prices[i-1]) / prices[i-1])
            indicators["volatility"] = float(np.std(returns)) if returns else 0.0
        
        return indicators
    
    @staticmethod
    def _calculate_ema(prices: List[float], period: int) -> float:
        """Calcule la moyenne mobile exponentielle."""
        if len(prices) < period:
            return float(np.mean(prices)) if prices else 0.0
        
        # Multiplicateur
        multiplier = 2 / (period + 1)
        
        # Première EMA = SMA
        ema = np.mean(prices[:period])
        
        # Calculer l'EMA pour les prix restants
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return float(ema)
    
    @staticmethod
    def get_signal_strength(indicators: Dict[str, float]) -> Dict[str, Any]:
        """Évalue la force des signaux techniques."""
        signals = {
            "buy_signals": [],
            "sell_signals": [],
            "neutral_signals": [],
            "overall_sentiment": "neutral"
        }
        
        # RSI
        rsi = indicators.get("rsi", 50)
        if rsi < 30:
            signals["buy_signals"].append(f"RSI oversold ({rsi:.1f})")
        elif rsi > 70:
            signals["sell_signals"].append(f"RSI overbought ({rsi:.1f})")
        else:
            signals["neutral_signals"].append(f"RSI neutral ({rsi:.1f})")
        
        # MACD
        macd = indicators.get("macd", 0)
        macd_signal = indicators.get("macd_signal", 0)
        if macd > macd_signal:
            signals["buy_signals"].append("MACD bullish")
        elif macd < macd_signal:
            signals["sell_signals"].append("MACD bearish")
        else:
            signals["neutral_signals"].append("MACD neutral")
        
        # Stochastique
        stoch_k = indicators.get("stoch_k", 50)
        if stoch_k < 20:
            signals["buy_signals"].append(f"Stochastic oversold ({stoch_k:.1f})")
        elif stoch_k > 80:
            signals["sell_signals"].append(f"Stochastic overbought ({stoch_k:.1f})")
        else:
            signals["neutral_signals"].append(f"Stochastic neutral ({stoch_k:.1f})")
        
        # Volume
        volume_ratio = indicators.get("volume_ratio", 1.0)
        if volume_ratio > 1.5:
            signals["buy_signals"].append(f"High volume ({volume_ratio:.1f}x)")
        elif volume_ratio < 0.5:
            signals["sell_signals"].append(f"Low volume ({volume_ratio:.1f}x)")
        
        # Déterminer le sentiment global
        buy_count = len(signals["buy_signals"])
        sell_count = len(signals["sell_signals"])
        
        if buy_count > sell_count:
            signals["overall_sentiment"] = "bullish"
        elif sell_count > buy_count:
            signals["overall_sentiment"] = "bearish"
        else:
            signals["overall_sentiment"] = "neutral"
        
        return signals
