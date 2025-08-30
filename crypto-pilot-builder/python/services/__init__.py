#!/usr/bin/env python3
"""
Package des services d'autowallet
"""

from .news_service import news_service, NewsItem, InvestmentAlert
from .ai_analyzer import ai_analyzer, MarketContext, AnalysisResult
from .alert_service import alert_service, AlertChannel, AlertTemplate
from .autowallet_service import autowallet_service, AutowalletConfig, TradeHistory

__all__ = [
    'news_service',
    'ai_analyzer', 
    'alert_service',
    'autowallet_service',
    'NewsItem',
    'InvestmentAlert',
    'MarketContext',
    'AnalysisResult',
    'AlertChannel',
    'AlertTemplate',
    'AutowalletConfig',
    'TradeHistory'
]
