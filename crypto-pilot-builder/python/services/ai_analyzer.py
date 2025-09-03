#!/usr/bin/env python3
"""
Service d'analyse IA pour l'autowallet
Analyse les news et génère des alertes d'investissement
"""

import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
import uuid
import os

from .news_service import NewsItem, InvestmentAlert, news_service

logger = logging.getLogger(__name__)

@dataclass
class MarketContext:
    """Contexte de marché pour l'analyse"""
    btc_dominance: float = 0.0
    market_sentiment: str = "neutral"  # bullish, bearish, neutral
    volatility_index: float = 0.0
    fear_greed_index: float = 50.0

@dataclass
class AnalysisResult:
    """Résultat d'analyse d'une news"""
    news_id: str
    crypto_symbol: str
    action: str  # buy, sell, hold
    confidence: float
    reasoning: str
    risk_level: str  # low, medium, high
    time_horizon: str  # short_term, medium_term, long_term
    price_target: Optional[float] = None

class AIAnalyzer:
    """Analyseur IA pour les décisions d'investissement"""
    
    def __init__(self):
        self.confidence_threshold = 0.3  # Seuil plus bas pour les tests
        self.risk_tolerance = "medium"  # low, medium, high
        self.investment_strategy = "balanced"  # conservative, balanced, aggressive
        
    def analyze_news_for_investment(self, news_items: List[NewsItem], 
                                  market_context: MarketContext = None) -> List[InvestmentAlert]:
        """Analyse les news et génère des alertes d'investissement"""
        alerts = []
        
        if not market_context:
            market_context = MarketContext()
        
        for news in news_items:
            # Traiter toutes les news, pas seulement celles avec un impact élevé
            analysis = self._analyze_single_news(news, market_context)
            if analysis and analysis.confidence >= self.confidence_threshold:
                alert = self._create_investment_alert(news, analysis)
                alerts.append(alert)
        
        return sorted(alerts, key=lambda x: x.confidence_score, reverse=True)
    
    def _analyze_single_news(self, news: NewsItem, market_context: MarketContext) -> Optional[AnalysisResult]:
        """Analyse une news individuelle"""
        try:
            # Analyse du sentiment
            sentiment_score = news.sentiment_score
            relevance_score = news.relevance_score
            
            # Décision d'action basée sur le sentiment et la pertinence
            if sentiment_score > 0.2 and relevance_score > 0.4:
                action = "buy"
                confidence = min(0.9, (sentiment_score + relevance_score) / 2)
            elif sentiment_score < -0.2 and relevance_score > 0.4:
                action = "sell"
                confidence = min(0.9, (abs(sentiment_score) + relevance_score) / 2)
            else:
                action = "hold"
                confidence = 0.5
            
            # Ajuster la confiance selon le contexte de marché (simplifié)
            if market_context:
                try:
                    confidence = self._adjust_confidence_by_market_context(
                        confidence, action, market_context
                    )
                except:
                    pass  # Ignorer les erreurs de contexte de marché
            
            # Raisonnement
            reasoning = self._generate_reasoning(news, action, confidence, market_context)
            
            # Niveau de risque
            risk_level = self._assess_risk_level(news, action, market_context)
            
            # Horizon temporel
            time_horizon = self._determine_time_horizon(news, action)
            
            # Cible de prix (estimation basique)
            price_target = self._estimate_price_target(news, action) if action != "hold" else None
            
            return AnalysisResult(
                news_id=news.id,
                crypto_symbol=news.crypto_mentions[0] if news.crypto_mentions else "BTC",
                action=action,
                confidence=confidence,
                reasoning=reasoning,
                risk_level=risk_level,
                time_horizon=time_horizon,
                price_target=price_target
            )
            
        except Exception as e:
            logger.error(f"Erreur lors de l'analyse de la news {news.id}: {e}")
            return None
    
    def _adjust_confidence_by_market_context(self, confidence: float, action: str, 
                                          market_context: MarketContext) -> float:
        """Ajuste la confiance selon le contexte de marché"""
        adjusted_confidence = confidence
        
        # Ajustement selon le sentiment du marché
        if market_context.market_sentiment == "bullish" and action == "buy":
            adjusted_confidence += 0.1
        elif market_context.market_sentiment == "bearish" and action == "sell":
            adjusted_confidence += 0.1
        elif market_context.market_sentiment == "bullish" and action == "sell":
            adjusted_confidence -= 0.2
        elif market_context.market_sentiment == "bearish" and action == "buy":
            adjusted_confidence -= 0.2
        
        # Ajustement selon l'indice de peur/avidité
        if market_context.fear_greed_index < 20 and action == "buy":  # Peur extrême
            adjusted_confidence += 0.15
        elif market_context.fear_greed_index > 80 and action == "sell":  # Avarice extrême
            adjusted_confidence += 0.15
        
        # Ajustement selon la volatilité
        if market_context.volatility_index > 0.8:  # Haute volatilité
            adjusted_confidence -= 0.1
        
        return max(0.1, min(0.95, adjusted_confidence))
    
    def _generate_reasoning(self, news: NewsItem, action: str, confidence: float, 
                           market_context: MarketContext) -> str:
        """Génère un raisonnement pour l'action d'investissement"""
        reasoning_parts = []
        
        # Base du raisonnement
        if action == "buy":
            reasoning_parts.append(f"Sentiment positif ({news.sentiment_score:.2f})")
            reasoning_parts.append(f"Pertinence élevée ({news.relevance_score:.2f})")
        elif action == "sell":
            reasoning_parts.append(f"Sentiment négatif ({news.sentiment_score:.2f})")
            reasoning_parts.append(f"Pertinence élevée ({news.relevance_score:.2f})")
        else:
            reasoning_parts.append("Sentiment neutre")
            reasoning_parts.append("Attendre plus d'informations")
        
        # Contexte de marché (sécurisé)
        if market_context and hasattr(market_context, 'market_sentiment') and market_context.market_sentiment != "neutral":
            reasoning_parts.append(f"Marché {market_context.market_sentiment}")
        
        if market_context and hasattr(market_context, 'fear_greed_index'):
            if market_context.fear_greed_index < 30:
                reasoning_parts.append("Indice de peur élevé (opportunité d'achat)")
            elif market_context.fear_greed_index > 70:
                reasoning_parts.append("Indice d'avidité élevé (risque de correction)")
        
        # Source de confiance
        if news.source.lower() in ['coindesk', 'cointelegraph', 'bitcoin.com']:
            reasoning_parts.append("Source fiable")
        
        return ". ".join(reasoning_parts)
    
    def _assess_risk_level(self, news: NewsItem, action: str, 
                          market_context: MarketContext) -> str:
        """Évalue le niveau de risque de l'investissement"""
        risk_score = 0
        
        # Risque basé sur la volatilité du marché (sécurisé)
        if market_context and hasattr(market_context, 'volatility_index'):
            if market_context.volatility_index > 0.8:
                risk_score += 2
            elif market_context.volatility_index > 0.5:
                risk_score += 1
        
        # Risque basé sur le sentiment
        if abs(news.sentiment_score) > 0.8:
            risk_score += 1
        
        # Risque basé sur l'action (sécurisé)
        if market_context and hasattr(market_context, 'fear_greed_index'):
            if action == "buy" and market_context.fear_greed_index > 80:
                risk_score += 1
            elif action == "sell" and market_context.fear_greed_index < 20:
                risk_score += 1
        
        # Risque basé sur la source
        if news.source.lower() not in ['coindesk', 'cointelegraph', 'bitcoin.com']:
            risk_score += 1
        
        if risk_score <= 1:
            return "low"
        elif risk_score <= 3:
            return "medium"
        else:
            return "high"
    
    def _determine_time_horizon(self, news: NewsItem, action: str) -> str:
        """Détermine l'horizon temporel de l'investissement"""
        if action == "hold":
            return "short_term"
        
        # Analyse du contenu pour déterminer l'horizon
        content = (news.title + ' ' + news.content).lower()
        
        long_term_keywords = ['adoption', 'partnership', 'regulation', 'institutional', 'long-term']
        medium_term_keywords = ['upgrade', 'update', 'launch', 'release', 'integration']
        short_term_keywords = ['pump', 'dump', 'breakout', 'crash', 'rally']
        
        if any(keyword in content for keyword in long_term_keywords):
            return "long_term"
        elif any(keyword in content for keyword in medium_term_keywords):
            return "medium_term"
        else:
            return "short_term"
    
    def _estimate_price_target(self, news: NewsItem, action: str) -> Optional[float]:
        """Estime une cible de prix (très basique)"""
        # Cette fonction est un placeholder pour une analyse plus sophistiquée
        # En production, elle utiliserait des données de prix historiques et des modèles ML
        
        if action == "buy":
            # Estimation optimiste : +10-30%
            return 1.15  # +15%
        elif action == "sell":
            # Estimation pessimiste : -10-30%
            return 0.85  # -15%
        
        return None
    
    def _create_investment_alert(self, news: NewsItem, analysis: AnalysisResult) -> InvestmentAlert:
        """Crée une alerte d'investissement"""
        # Déterminer la priorité
        if analysis.confidence > 0.85 and analysis.risk_level == "low":
            priority = "urgent"
        elif analysis.confidence > 0.75:
            priority = "high"
        elif analysis.confidence > 0.65:
            priority = "medium"
        else:
            priority = "low"
        
        return InvestmentAlert(
            id=str(uuid.uuid4()),
            news_id=news.id,
            crypto_symbol=analysis.crypto_symbol,
            alert_type=analysis.action,
            confidence_score=analysis.confidence,
            reasoning=analysis.reasoning,
            created_at=datetime.now(),
            priority=priority
        )
    
    def get_market_context(self) -> MarketContext:
        """Récupère le contexte de marché actuel"""
        # En production, cette fonction récupérerait des données en temps réel
        # Pour l'instant, on utilise des valeurs par défaut
        return MarketContext(
            btc_dominance=45.0,
            market_sentiment="neutral",
            volatility_index=0.6,
            fear_greed_index=55.0
        )
    
    def update_strategy_settings(self, confidence_threshold: float = None, 
                               risk_tolerance: str = None, 
                               investment_strategy: str = None):
        """Met à jour les paramètres de stratégie"""
        if confidence_threshold is not None:
            self.confidence_threshold = max(0.1, min(0.95, confidence_threshold))
        
        if risk_tolerance in ["low", "medium", "high"]:
            self.risk_tolerance = risk_tolerance
        
        if investment_strategy in ["conservative", "balanced", "aggressive"]:
            self.investment_strategy = investment_strategy

# Instance singleton
ai_analyzer = AIAnalyzer()
