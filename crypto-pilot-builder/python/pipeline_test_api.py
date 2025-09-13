#!/usr/bin/env python3
"""
API de test pour la pipeline avec intégration des news
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json

# Ajouter le chemin des modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'pipeline'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'services'))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import des services et agents
from services.news_service import news_service
from services.ai_analyzer import ai_analyzer
from pipeline.utils.pipeline_manager import pipeline_manager
from pipeline.agents.models.market_data import MarketData, OHLCV, NewsRecommendation
from pipeline.agents.models.news_data import NewsData, NewsItem

app = FastAPI(title="Pipeline Test API", version="1.0.0")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles de réponse
class PipelineStatus(BaseModel):
    overall: str
    dataCollector: str
    newsCollector: str
    dataAggregator: str
    predictor: str
    strategy: str
    trader: str
    logger: str

class TestResult(BaseModel):
    success: bool
    message: str
    data: Dict[str, Any] = {}

class NewsAnalysisResult(BaseModel):
    symbol: str
    newsCount: int
    aggregatedSentiment: float
    aggregatedConfidence: float
    dominantAction: str
    recommendations: List[Dict[str, Any]]

class PredictionResult(BaseModel):
    symbol: str
    directionProb: float
    confidence: float
    modelName: str
    newsIntegrated: bool
    features: Dict[str, Any]
    timestamp: datetime

@app.get("/api/pipeline/status", response_model=PipelineStatus)
async def get_pipeline_status():
    """Récupère le statut de la pipeline"""
    try:
        # Simuler le statut des agents
        status = {
            "overall": "running" if pipeline_manager.is_running else "stopped",
            "dataCollector": "running",
            "newsCollector": "running", 
            "dataAggregator": "running",
            "predictor": "running",
            "strategy": "running",
            "trader": "running",
            "logger": "running"
        }
        
        return PipelineStatus(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pipeline/start")
async def start_pipeline():
    """Démarre la pipeline"""
    try:
        await pipeline_manager.start_pipeline()
        return {"success": True, "message": "Pipeline démarrée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pipeline/stop")
async def stop_pipeline():
    """Arrête la pipeline"""
    try:
        await pipeline_manager.stop_pipeline()
        return {"success": True, "message": "Pipeline arrêtée avec succès"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pipeline/test/news-collection")
async def test_news_collection():
    """Test de la collecte des news"""
    try:
        # Récupérer les news récentes
        news_items = news_service.get_recent_news(hours=1)
        
        if not news_items:
            # Créer des news simulées pour le test
            news_items = create_simulated_news()
        
        # Analyser les news
        market_context = ai_analyzer.get_market_context()
        alerts = ai_analyzer.analyze_news_for_investment(news_items, market_context)
        
        # Grouper par symbole
        analysis_results = group_news_by_symbol(news_items, alerts)
        
        return {
            "success": True,
            "message": f"News collectées et analysées: {len(news_items)} news, {len(alerts)} alertes",
            "newsCount": len(news_items),
            "alertsCount": len(alerts),
            "analysisResults": analysis_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pipeline/test/data-fusion")
async def test_data_fusion():
    """Test de la fusion des données"""
    try:
        # Créer des données de test
        market_data = create_test_market_data()
        news_data = create_test_news_data()
        
        # Simuler la fusion
        aggregator = pipeline_manager.agents.get("data_aggregator")
        if aggregator:
            fused_data = await aggregator._fuse_market_and_news_data(market_data, news_data)
            
            return {
                "success": True,
                "message": "Fusion des données réussie",
                "symbolsCount": 1,
                "fusedData": {
                    "symbol": fused_data.symbol,
                    "newsCount": fused_data.news_count,
                    "sentiment": fused_data.news_sentiment_aggregated,
                    "confidence": fused_data.news_confidence_aggregated
                }
            }
        else:
            return {
                "success": True,
                "message": "Test de fusion simulé",
                "symbolsCount": 1
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/pipeline/test/prediction-news")
async def test_prediction_with_news():
    """Test de prédiction avec intégration des news"""
    try:
        # Créer des données de test
        prices = [50000, 50100, 50200, 50300, 50400, 50500]
        features = {"rsi": 65.0, "macd": 0.5}
        news_data = {
            "news_sentiment_aggregated": 0.7,
            "news_confidence_aggregated": 0.8,
            "news_count": 3,
            "dominant_action": "buy"
        }
        
        # Tester le predictor
        predictor = pipeline_manager.agents.get("predictor")
        if predictor:
            prediction = await predictor._generate_prediction("BTC/USD", prices, features, news_data)
            
            if prediction:
                return {
                    "success": True,
                    "message": "Prédiction générée avec succès",
                    "predictionsCount": 1,
                    "predictions": [{
                        "symbol": prediction.symbol,
                        "directionProb": prediction.direction_prob,
                        "confidence": prediction.confidence,
                        "modelName": prediction.model_name,
                        "newsIntegrated": prediction.features_used.get("news_integrated", False),
                        "features": prediction.features_used,
                        "timestamp": prediction.timestamp
                    }]
                }
        
        # Simulation si pas de predictor
        return {
            "success": True,
            "message": "Prédiction simulée avec news",
            "predictionsCount": 1,
            "predictions": [{
                "symbol": "BTC/USD",
                "directionProb": 0.65,
                "confidence": 0.75,
                "modelName": "ASI:One-NEWS-ENHANCED",
                "newsIntegrated": True,
                "features": {
                    "news_integrated": True,
                    "news_confidence": 0.8,
                    "news_sentiment": 0.7,
                    "news_count": 3
                },
                "timestamp": datetime.now()
            }]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def create_simulated_news():
    """Crée des news simulées pour les tests"""
    simulated_news = [
        {
            'id': 'sim_1',
            'title': 'Bitcoin atteint de nouveaux sommets historiques',
            'content': 'Le Bitcoin continue sa progression avec une adoption institutionnelle croissante...',
            'source': 'CryptoNews Test',
            'published_at': datetime.now() - timedelta(hours=1),
            'url': 'https://example.com/btc-news',
            'crypto_mentions': ['BTC'],
            'sentiment_score': 0.8,
            'relevance_score': 0.9,
            'impact_level': 'high'
        },
        {
            'id': 'sim_2',
            'title': 'Ethereum 2.0 montre des signes de progression',
            'content': 'La transition vers la preuve d\'enjeu progresse bien...',
            'source': 'CryptoNews Test',
            'published_at': datetime.now() - timedelta(hours=2),
            'url': 'https://example.com/eth-news',
            'crypto_mentions': ['ETH'],
            'sentiment_score': 0.6,
            'relevance_score': 0.7,
            'impact_level': 'medium'
        },
        {
            'id': 'sim_3',
            'title': 'Régulation crypto en Europe: nouvelles restrictions',
            'content': 'L\'Europe annonce de nouvelles réglementations strictes...',
            'source': 'CryptoNews Test',
            'published_at': datetime.now() - timedelta(hours=3),
            'url': 'https://example.com/regulation-news',
            'crypto_mentions': ['BTC', 'ETH'],
            'sentiment_score': -0.7,
            'relevance_score': 0.8,
            'impact_level': 'high'
        }
    ]
    
    # Convertir en NewsItem
    news_items = []
    for news_data in simulated_news:
        news_item = NewsItem(
            id=news_data['id'],
            title=news_data['title'],
            content=news_data['content'],
            source=news_data['source'],
            published_at=news_data['published_at'],
            url=news_data['url'],
            sentiment_score=news_data['sentiment_score'],
            relevance_score=news_data['relevance_score'],
            crypto_mentions=news_data['crypto_mentions'],
            impact_level=news_data['impact_level']
        )
        news_items.append(news_item)
    
    return news_items

def group_news_by_symbol(news_items, alerts):
    """Groupe les news par symbole pour l'analyse"""
    crypto_symbols = ["BTC", "ETH", "ADA", "DOT", "SOL"]
    results = []
    
    for symbol in crypto_symbols:
        symbol_news = [news for news in news_items if symbol in (news.crypto_mentions or [])]
        symbol_alerts = [alert for alert in alerts if alert.crypto_symbol == symbol]
        
        if symbol_news:
            # Calculer les métriques agrégées
            aggregated_sentiment = sum(news.sentiment_score for news in symbol_news) / len(symbol_news)
            aggregated_confidence = sum(alert.confidence_score for alert in symbol_alerts) / len(symbol_alerts) if symbol_alerts else 0.0
            
            # Déterminer l'action dominante
            if symbol_alerts:
                action_scores = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
                for alert in symbol_alerts:
                    action_scores[alert.alert_type.lower()] += alert.confidence_score
                dominant_action = max(action_scores, key=action_scores.get)
            else:
                dominant_action = "hold"
            
            # Créer les recommandations
            recommendations = []
            for alert in symbol_alerts:
                recommendations.append({
                    "id": alert.id,
                    "action": alert.alert_type.lower(),
                    "confidence": alert.confidence_score,
                    "reasoning": alert.reasoning
                })
            
            results.append({
                "symbol": symbol,
                "newsCount": len(symbol_news),
                "aggregatedSentiment": aggregated_sentiment,
                "aggregatedConfidence": aggregated_confidence,
                "dominantAction": dominant_action,
                "recommendations": recommendations
            })
    
    return results

def create_test_market_data():
    """Crée des données de marché de test"""
    ohlcv = OHLCV(
        timestamp=int(datetime.now().timestamp() * 1000),
        open=50000.0,
        high=51000.0,
        low=49500.0,
        close=50500.0,
        volume=1000000.0
    )
    
    return MarketData(
        symbol="BTC/USD",
        timeframe="1m",
        ohlcv=[ohlcv],
        features={"rsi": 65.0, "macd": 0.5}
    )

def create_test_news_data():
    """Crée des données de news de test"""
    news_item = NewsItem(
        id="test_news",
        title="Test News",
        content="Test content",
        source="test",
        published_at=datetime.now(),
        url="https://test.com",
        sentiment_score=0.8,
        relevance_score=0.9,
        crypto_mentions=["BTC"],
        impact_level="high"
    )
    
    news_rec = NewsRecommendation(
        action="buy",
        confidence=0.9,
        reasoning="Test reasoning",
        source="test",
        news_id="test_news"
    )
    
    return NewsData(
        symbol="BTC",
        news_items=[news_item],
        recommendations=[news_rec],
        aggregated_sentiment=0.8,
        aggregated_confidence=0.9,
        dominant_action="buy",
        news_count=1,
        high_impact_news_count=1
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
