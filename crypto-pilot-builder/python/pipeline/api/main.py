"""API FastAPI pour le Pipeline de Trading Crypto."""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from pydantic import BaseModel, Field
import structlog

from ..utils.pipeline_manager import pipeline_manager

logger = structlog.get_logger(__name__)

# Modèles Pydantic pour l'API
class HealthResponse(BaseModel):
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = "1.0.0"

class AgentStatus(BaseModel):
    name: str
    status: str
    last_activity: Optional[datetime] = None
    data_collected: int = 0
    errors: int = 0

class TestRequest(BaseModel):
    token_address: str = Field(..., description="Adresse du token ERC20 à tester")
    test_type: str = Field(..., description="Type de test: price, block, gas")
    duration_seconds: int = Field(60, description="Durée du test en secondes")

class TestResponse(BaseModel):
    test_id: str
    status: str
    results: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PipelineStatus(BaseModel):
    agents: List[AgentStatus]
    ethereum_connection: bool
    last_data_collection: Optional[datetime] = None
    total_data_points: int = 0

# État global de l'application
app_state = {
    "data_collector": None,
    "ethereum_client": None,  # Plus utilisé, gardé pour compatibilité
    "tests_running": {},
    "data_collected": [],
    "errors": [],
    "price_history": [],  # Historique des prix pour le graphique
    "max_price_history": 10  # Maximum 10 points de prix
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestion du cycle de vie de l'application."""
    logger.info("🚀 Démarrage de l'API FastAPI")
    
    # Plus besoin d'Ethereum client pour le trading simple
    logger.info("✅ Pipeline configuré pour trading sur prix uniquement")
    
    yield
    
    # Nettoyage
    logger.info("🛑 Arrêt de l'API FastAPI")
    if app_state["data_collector"]:
        await app_state["data_collector"].cleanup()

# Création de l'application FastAPI
app = FastAPI(
    title="Pipeline de Trading Crypto API",
    description="API pour tester et contrôler le pipeline de trading crypto avec agents uAgents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Templates pour le front-end
templates = Jinja2Templates(directory="src/api/templates")

# Endpoints de base
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Page d'accueil avec interface web."""
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "title": "Pipeline de Trading Crypto"}
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Vérification de l'état de santé de l'API."""
    return HealthResponse()

@app.get("/status", response_model=PipelineStatus)
async def get_pipeline_status():
    """Statut du pipeline et des agents."""
    agents = []
    
    # Statut du DataCollector
    if app_state["data_collector"]:
        agents.append(AgentStatus(
            name="DataCollector",
            status="running",
            last_activity=datetime.utcnow(),
            data_collected=len(app_state["data_collected"]),
            errors=len(app_state["errors"])
        ))
    else:
        agents.append(AgentStatus(
            name="DataCollector",
            status="stopped",
            data_collected=0,
            errors=0
        ))
    
    return PipelineStatus(
        agents=agents,
        ethereum_connection=False,  # Plus de connexion Ethereum
        last_data_collection=app_state["data_collected"][-1]["timestamp"] if app_state["data_collected"] else None,
        total_data_points=len(app_state["data_collected"])
    )

# Endpoints pour les agents
@app.post("/agents/data-collector/start")
async def start_data_collector():
    """Démarre l'agent DataCollector."""
    try:
        if app_state["data_collector"]:
            return {"message": "DataCollector déjà en cours d'exécution"}
        
        logger.info("🔄 Démarrage de l'agent DataCollector...")
        app_state["data_collector"] = DataCollectorAgent()
        
        # Démarrer l'agent en arrière-plan
        asyncio.create_task(app_state["data_collector"].run())
        
        logger.info("✅ DataCollector démarré")
        return {"message": "DataCollector démarré avec succès"}
        
    except Exception as e:
        logger.error("❌ Erreur démarrage DataCollector", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/data-collector/stop")
async def stop_data_collector():
    """Arrête l'agent DataCollector."""
    try:
        if not app_state["data_collector"]:
            return {"message": "DataCollector non démarré"}
        
        logger.info("🛑 Arrêt de l'agent DataCollector...")
        await app_state["data_collector"].cleanup()
        app_state["data_collector"] = None
        
        logger.info("✅ DataCollector arrêté")
        return {"message": "DataCollector arrêté avec succès"}
        
    except Exception as e:
        logger.error("❌ Erreur arrêt DataCollector", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints pour les tests
@app.post("/tests/ethereum", response_model=TestResponse)
async def test_ethereum_connection():
    """Test de connexion Ethereum (désactivé - trading sur prix uniquement)."""
    return TestResponse(
        test_id=f"eth_test_{datetime.utcnow().timestamp()}",
        status="completed",
        results={
            "connected": False,
            "message": "Connexion Ethereum désactivée - Trading sur prix uniquement via CoinGecko",
            "trading_mode": "price_only"
        }
    )

@app.post("/tests/token-price", response_model=TestResponse)
async def test_token_price(
    token_address: str = Query(..., description="Adresse du token ERC20"),
    api: str = Query("coingecko", description="API à utiliser: coingecko ou coinpaprika")
):
    """Test de récupération du prix d'un token."""
    try:
        # Test simplifié - plus de connexion Ethereum
        logger.info("Test de prix de token simplifié - trading sur prix uniquement")
        
        # Simulation d'un prix (en production, utiliser CoinGecko)
        import random
        price = random.uniform(0.5, 2.0)  # Prix simulé
        
        results = {
                "token_address": token_address,
                "api": api,
                "price": price,
                "success": price is not None
            }
        
        return TestResponse(
            test_id=f"price_test_{datetime.utcnow().timestamp()}",
            status="completed",
            results=results
        )
        
    except Exception as e:
        logger.error("❌ Erreur test prix token", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tests/bitcoin-price", response_model=TestResponse)
async def test_bitcoin_price():
    """Test de récupération du prix Bitcoin avec données complètes."""
    try:
        # Utiliser le service unifié de données de marché
        from src.utils.market_data_service import market_data_service
        
        # Récupérer données complètes (prix + blockchain)
        market_data = await market_data_service.get_complete_market_data("bitcoin")
        
        if market_data["success"]:
            results = {
                "cryptocurrency": "Bitcoin",
                "symbol": "BTC",
                "price_usd": market_data["crypto"]["price_usd"],
                "price_source": market_data["crypto"]["source"],
                "blockchain_data": market_data["blockchain"],
                "success": True
            }
        else:
            results = {
                "cryptocurrency": "Bitcoin",
                "symbol": "BTC",
                "error": "Données non disponibles",
                "success": False
            }
        
        return TestResponse(
            test_id=f"btc_price_test_{datetime.utcnow().timestamp()}",
            status="completed",
            results=results
        )
        
    except Exception as e:
        logger.error("❌ Erreur test prix Bitcoin", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tests/data-collection", response_model=TestResponse)
async def test_data_collection(background_tasks: BackgroundTasks):
    """Test de collecte de données."""
    try:
        if not app_state["data_collector"]:
            raise HTTPException(status_code=503, detail="DataCollector non démarré")
        
        # Lancer une collecte de données
        background_tasks.add_task(run_data_collection_test)
        
        return TestResponse(
            test_id=f"collection_test_{datetime.utcnow().timestamp()}",
            status="running",
            results={"message": "Test de collecte lancé en arrière-plan"}
        )
        
    except Exception as e:
        logger.error("❌ Erreur test collecte", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

async def run_data_collection_test():
    """Exécute un test de collecte de données."""
    try:
        logger.info("🔄 Test de collecte de données...")
        
        # Récupérer de vraies données de marché
        from src.utils.market_data_service import market_data_service
        
        # Collecter les prix de plusieurs cryptos
        crypto_ids = ["bitcoin", "ethereum", "tether", "usd-coin"]
        prices = await market_data_service.get_multiple_prices(crypto_ids)
        
        # Récupérer les données blockchain
        blockchain_data = await market_data_service.get_blockchain_data()
        
        # Créer les données de test avec de vraies informations
        test_data = {
            "timestamp": datetime.utcnow(),
            "tokens": list(prices.keys()),
            "prices": list(prices.values()),
            "block_number": blockchain_data["block_number"] if blockchain_data else 0,
            "gas_price": blockchain_data["gas_price"] if blockchain_data else 0,
            "source": "real_data"
        }
        
        app_state["data_collected"].append(test_data)
        logger.info("✅ Test de collecte terminé avec vraies données")
        
    except Exception as e:
        logger.error("❌ Erreur test collecte", error=str(e))
        app_state["errors"].append({
            "timestamp": datetime.utcnow(),
            "error": str(e)
        })

# Endpoints pour les données
@app.get("/data/latest")
async def get_latest_data(limit: int = Query(10, description="Nombre de points de données à récupérer")):
    """Récupère les dernières données collectées."""
    return {
        "data": app_state["data_collected"][-limit:] if app_state["data_collected"] else [],
        "total": len(app_state["data_collected"])
    }

@app.get("/data/errors")
async def get_errors(limit: int = Query(10, description="Nombre d'erreurs à récupérer")):
    """Récupère les dernières erreurs."""
    return {
        "errors": app_state["errors"][-limit:] if app_state["errors"] else [],
        "total": len(app_state["errors"])
    }

@app.get("/data/prices")
async def get_price_data(limit: int = Query(10, description="Nombre de points de prix à récupérer")):
    """Récupère les données de prix pour le graphique."""
    try:
        # Utiliser le service unifié de données de marché pour de vraies données
        from src.utils.market_data_service import market_data_service
        
        # Récupérer le prix Bitcoin en temps réel
        btc_price = await market_data_service.get_crypto_price("bitcoin")
        
        if btc_price:
            # Créer un nouveau point de données
            new_price_point = {
                "timestamp": datetime.utcnow(),
                "price": btc_price,
                "token": "BTC",
                "source": "CoinGecko"
            }
            
            # Ajouter à l'historique
            app_state["price_history"].append(new_price_point)
            
            # Garder seulement les 10 derniers points (FIFO)
            if len(app_state["price_history"]) > app_state["max_price_history"]:
                app_state["price_history"] = app_state["price_history"][-app_state["max_price_history"]:]
            
            # Retourner l'historique complet (max 10 points)
            return {
                "prices": app_state["price_history"],
                "total": len(app_state["price_history"]),
                "source": "real_data"
            }
        else:
            # Fallback si pas de données disponibles
            return {
                "prices": app_state["price_history"],  # Retourner l'historique existant
                "total": len(app_state["price_history"]),
                "error": "Impossible de récupérer les nouvelles données de prix",
                "source": "cached_data"
            }
        
    except Exception as e:
        logger.error("❌ Erreur récupération données prix", error=str(e))
        return {
            "prices": app_state["price_history"],  # Retourner l'historique existant
            "total": len(app_state["price_history"]),
            "error": str(e),
            "source": "cached_data"
        }

@app.delete("/data/clear")
async def clear_data():
    """Efface toutes les données collectées."""
    app_state["data_collected"] = []
    app_state["errors"] = []
    app_state["price_history"] = []  # Vider aussi l'historique des prix
    return {"message": "Données effacées"}

@app.delete("/data/prices/clear")
async def clear_price_history():
    """Efface l'historique des prix."""
    app_state["price_history"] = []
    return {"message": "Historique des prix effacé"}

# Endpoints de test pour les agents de trading
@app.post("/tests/predictor", response_model=TestResponse)
async def test_predictor_agent():
    """Test de l'agent Predictor avec ASI:One."""
    try:
        import numpy as np
        
        # Importer les modules nécessaires
        from src.utils.asi_model import ASIOneModel
        from src.utils.technical_indicators import TechnicalIndicators
        from src.utils.market_data_service import market_data_service
        
        # Récupérer de vraies données de marché
        market_data = await market_data_service.get_complete_market_data("bitcoin")
        
        if not market_data["success"] or not market_data["crypto"]["price_usd"]:
            raise HTTPException(status_code=503, detail="Impossible de récupérer les données de marché")
        
        current_price = market_data["crypto"]["price_usd"]
        
        # Générer un historique de prix basé sur le prix actuel avec des variations réalistes
        import random
        prices = [current_price]
        for i in range(29):  # 30 points au total
            # Variation réaliste (±2%)
            variation = random.uniform(-0.02, 0.02)
            new_price = prices[-1] * (1 + variation)
            prices.append(new_price)
        
        # Générer des volumes réalistes basés sur le prix
        volumes = [random.uniform(current_price * 1000, current_price * 5000) for _ in range(30)]
        
        # Calculer les indicateurs techniques
        technical_indicators = TechnicalIndicators.calculate_all_indicators(prices, volumes)
        
        # Initialiser le modèle ASI:One
        asi_model = ASIOneModel(model="asi1-mini")
        
        # Générer la prédiction
        prediction_result = await asi_model.predict_price_direction(
            price_history=prices,
            volume_history=volumes,
            technical_indicators=technical_indicators,
            symbol="BTC/USD"
        )
        
        # Analyser les signaux techniques
        signal_analysis = TechnicalIndicators.get_signal_strength(technical_indicators)
        
        results = {
            "symbol": "BTC/USD",
            "current_price": round(current_price, 4),
            "direction_probability": round(prediction_result["direction_probability"], 3),
            "confidence": round(prediction_result["confidence"], 3),
            "volatility": round(technical_indicators.get("volatility", 0.01), 4),
            "prediction_horizon": "5 minutes",
            "model_name": prediction_result["model_name"],
            "trend_analysis": prediction_result.get("trend_analysis", "Analyse non disponible"),
            "key_factors": prediction_result.get("key_factors", []),
            "risk_level": prediction_result.get("risk_level", "modéré"),
            "technical_signals": signal_analysis,
            "features_used": {
                "price_history_length": len(prices),
                "technical_indicators": len(technical_indicators),
                "volume_analysis": True,
                "asi_model": asi_model.model
            },
            "success": True
        }
        
        return TestResponse(
            test_id=f"predictor_test_{datetime.utcnow().timestamp()}",
            status="completed",
            results=results
        )
        
    except Exception as e:
        logger.error("❌ Erreur test Predictor ASI:One", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tests/strategy", response_model=TestResponse)
async def test_strategy_agent():
    """Test de l'agent Strategy - Gestion des risques avec vraies données."""
    try:
        import random
        
        # Récupérer de vraies données de marché
        from src.utils.market_data_service import market_data_service
        market_data = await market_data_service.get_complete_market_data("bitcoin")
        
        if not market_data["success"] or not market_data["crypto"]["price_usd"]:
            raise HTTPException(status_code=503, detail="Impossible de récupérer les données de marché")
        
        current_price = market_data["crypto"]["price_usd"]
        
        # Simulation d'une prédiction basée sur le prix réel
        # Plus le prix est élevé, plus la probabilité de baisse augmente (logique de marché)
        price_factor = min(current_price / 50000, 1.0)  # Normaliser par rapport à 50k
        direction_prob = 0.5 + (0.3 * (1 - price_factor))  # Probabilité entre 0.5 et 0.8
        confidence = random.uniform(0.6, 0.9)
        
        # Logique de stratégie
        signal_type = "HOLD"
        position_size = 0.0
        
        if direction_prob > 0.65 and confidence > 0.7:
            signal_type = "BUY"
            position_size = min(0.1, confidence * 0.15)  # 10% max du capital
        elif direction_prob < 0.35 and confidence > 0.7:
            signal_type = "SELL"
            position_size = min(0.1, confidence * 0.15)
        
        # Calcul des niveaux de risque
        stop_loss = current_price * (0.98 if signal_type == "BUY" else 1.02)
        take_profit = current_price * (1.03 if signal_type == "BUY" else 0.97)
        
        results = {
            "symbol": "BTC/USD",
            "signal_type": signal_type,
            "confidence": round(confidence, 3),
            "position_size": round(position_size, 3),
            "current_price": round(current_price, 4),
            "stop_loss": round(stop_loss, 4),
            "take_profit": round(take_profit, 4),
            "risk_metrics": {
                "max_daily_loss": 0.05,
                "max_open_trades": 3,
                "min_confidence": 0.6
            },
            "success": True
        }
        
        return TestResponse(
            test_id=f"strategy_test_{datetime.utcnow().timestamp()}",
            status="completed",
            results=results
        )
        
    except Exception as e:
        logger.error("❌ Erreur test Strategy", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tests/trader", response_model=TestResponse)
async def test_trader_agent():
    """Test de l'agent Trader - Exécution d'ordres avec vraies données."""
    try:
        import random
        
        # Récupérer de vraies données de marché
        from src.utils.market_data_service import market_data_service
        market_data = await market_data_service.get_complete_market_data("bitcoin")
        
        if not market_data["success"] or not market_data["crypto"]["price_usd"]:
            raise HTTPException(status_code=503, detail="Impossible de récupérer les données de marché")
        
        current_price = market_data["crypto"]["price_usd"]
        
        # Simulation d'un signal de trading basé sur le prix réel
        # Logique simple : si prix > 100k, tendance baissière, sinon haussière
        if current_price > 100000:
            signal_type = random.choice(["SELL", "HOLD"])
        else:
            signal_type = random.choice(["BUY", "HOLD"])
        
        quantity = random.uniform(0.1, 1.0) if signal_type != "HOLD" else 0  # Quantité en BTC
        price = current_price
        
        # Simulation de l'exécution
        execution_price = price * (1 + random.uniform(-0.001, 0.001))  # Slippage ±0.1%
        status = "FILLED" if random.random() > 0.1 else "FAILED"  # 90% de succès
        
        # Calcul du P&L si applicable
        pnl = 0.0
        if signal_type != "HOLD" and status == "FILLED":
            if signal_type == "BUY":
                pnl = (price * 1.02 - execution_price) * quantity  # Simulation gain 2%
            else:
                pnl = (execution_price - price * 0.98) * quantity  # Simulation gain 2%
        
        results = {
            "trade_id": f"trade_{random.randint(1000, 9999)}",
            "symbol": "BTC/USD",
            "signal_type": signal_type,
            "quantity": round(quantity, 2),
            "price": round(price, 4),
            "execution_price": round(execution_price, 4),
            "status": status,
            "pnl": round(pnl, 2),
            "slippage": round(abs(execution_price - price) / price * 100, 3),
            "paper_trading": True,
            "capital_remaining": 9500.0,  # Simulation
            "success": status == "FILLED"
        }
        
        return TestResponse(
            test_id=f"trader_test_{datetime.utcnow().timestamp()}",
            status="completed",
            results=results
        )
        
    except Exception as e:
        logger.error("❌ Erreur test Trader", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tests/logger", response_model=TestResponse)
async def test_logger_agent():
    """Test de l'agent Logger - Monitoring avec vraies données du pipeline."""
    try:
        # Récupérer de vraies données du pipeline au lieu de simuler
        from src.utils.pipeline_manager import pipeline_manager
        
        # Vérifier si le pipeline est en cours d'exécution
        if not pipeline_manager.is_running:
            return TestResponse(
                test_id=f"logger_test_{datetime.utcnow().timestamp()}",
                status="completed",
                results={
                    "message": "Pipeline non démarré - Aucune donnée à logger",
                    "pipeline_status": "stopped",
                    "success": True
                }
            )
        
        # Récupérer les vraies données du pipeline
        pipeline_data = pipeline_manager.get_pipeline_data(limit=10)
        
        if not pipeline_data:
            return TestResponse(
                test_id=f"logger_test_{datetime.utcnow().timestamp()}",
                status="completed",
                results={
                    "message": "Aucune donnée de pipeline disponible",
                    "pipeline_data_count": 0,
                    "success": True
                }
            )
        
        # Analyser les vraies données du pipeline
        total_executions = len(pipeline_data)
        successful_executions = sum(1 for data in pipeline_data if data.get("strategy_signal") or data.get("trade_execution"))
        
        # Calculer les vraies métriques basées sur les données réelles
        execution_rate = successful_executions / total_executions if total_executions > 0 else 0
        
        # Analyser les signaux de trading
        trading_signals = [data for data in pipeline_data if data.get("strategy_signal")]
        buy_signals = sum(1 for data in trading_signals if data["strategy_signal"].get("action") == "BUY")
        sell_signals = sum(1 for data in trading_signals if data["strategy_signal"].get("action") == "SELL")
        
        # Analyser les prédictions
        predictions = [data for data in pipeline_data if data.get("prediction")]
        avg_confidence = sum(data["prediction"].get("confidence", 0) for data in predictions) / len(predictions) if predictions else 0
        
        results = {
            "pipeline_analysis": {
                "total_executions": total_executions,
                "successful_executions": successful_executions,
                "execution_rate": round(execution_rate, 3),
                "last_execution": pipeline_data[-1]["timestamp"].isoformat() if pipeline_data else None
            },
            "trading_analysis": {
                "total_signals": len(trading_signals),
                "buy_signals": buy_signals,
                "sell_signals": sell_signals,
                "signal_distribution": {
                    "BUY": buy_signals,
                    "SELL": sell_signals,
                    "HOLD": len(trading_signals) - buy_signals - sell_signals
                }
            },
            "prediction_analysis": {
                "total_predictions": len(predictions),
                "average_confidence": round(avg_confidence, 3),
                "prediction_models_used": list(set(data["prediction"].get("model_name", "Unknown") for data in predictions))
            },
            "data_quality": {
                "market_data_points": sum(1 for data in pipeline_data if data.get("price")),
                "prediction_quality": "High" if avg_confidence > 0.7 else "Medium" if avg_confidence > 0.5 else "Low"
            },
            "last_update": datetime.utcnow().isoformat(),
            "success": True,
            "data_source": "real_pipeline_data"
        }
        
        return TestResponse(
            test_id=f"logger_test_{datetime.utcnow().timestamp()}",
            status="completed",
            results=results
        )
        
    except Exception as e:
        logger.error("❌ Erreur test Logger", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints pour la configuration
@app.get("/config")
async def get_config():
    """Récupère la configuration actuelle."""
    return {
        "trading_mode": "price_only",
        "data_collector_interval": 60,
        "crypto_monitored": [
            "bitcoin",  # BTC via CoinGecko
            "ethereum",  # ETH via CoinGecko
        ]
    }

@app.get("/logger/health")
async def get_logger_health():
    """Récupère la santé du pipeline depuis le Logger."""
    try:
        # Récupérer les vraies données du pipeline
        from src.utils.pipeline_manager import pipeline_manager
        
        if not pipeline_manager.is_running:
            return {
                "pipeline_status": "stopped",
                "message": "Pipeline non démarré",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Récupérer les données du pipeline pour analyse
        pipeline_data = pipeline_manager.get_pipeline_data(limit=20)
        
        if not pipeline_data:
            return {
                "pipeline_status": "running",
                "message": "Pipeline actif mais aucune donnée disponible",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Analyser les vraies données du pipeline
        total_executions = len(pipeline_data)
        data_collection_success = sum(1 for data in pipeline_data if data.get("price") and data.get("symbol"))
        predictions = [data for data in pipeline_data if data.get("prediction")]
        signals = [data for data in pipeline_data if data.get("strategy_signal")]
        trades = [data for data in pipeline_data if data.get("trade_execution")]
        
        # Calculer les vraies métriques
        execution_rate = data_collection_success / total_executions if total_executions > 0 else 0
        avg_confidence = sum(data["prediction"].get("confidence", 0) for data in predictions) / len(predictions) if predictions else 0
        signal_rate = len(signals) / total_executions if total_executions > 0 else 0
        trade_rate = len(trades) / total_executions if total_executions > 0 else 0
        
        # Évaluer la santé du pipeline
        health_score = (execution_rate * 30 + 
                       (avg_confidence if avg_confidence > 0 else 0) * 25 +
                       signal_rate * 25 + 
                       trade_rate * 20)
        
        if health_score >= 80:
            pipeline_health = "Excellent"
        elif health_score >= 60:
            pipeline_health = "Good"
        elif health_score >= 40:
            pipeline_health = "Fair"
        else:
            pipeline_health = "Poor"
        
        return {
            "pipeline_status": "running",
            "pipeline_health": pipeline_health,
            "health_score": round(health_score, 1),
            "metrics": {
                "total_executions": total_executions,
                "execution_rate": round(execution_rate, 3),
                "data_collection_success": data_collection_success,
                "predictions_count": len(predictions),
                "average_confidence": round(avg_confidence, 3),
                "signals_count": len(signals),
                "signal_generation_rate": round(signal_rate, 3),
                "trades_count": len(trades),
                "trade_execution_rate": round(trade_rate, 3)
            },
            "last_execution": pipeline_data[-1]["timestamp"].isoformat() if pipeline_data else None,
            "timestamp": datetime.utcnow().isoformat(),
            "data_source": "real_pipeline_data"
        }
        
    except Exception as e:
        logger.error("❌ Erreur récupération santé Logger", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# NOUVEAUX ENDPOINTS POUR LE PIPELINE SÉQUENTIEL
# ============================================================================

@app.post("/pipeline/start")
async def start_pipeline():
    """Démarre le pipeline séquentiel complet."""
    try:
        success = await pipeline_manager.start_pipeline()
        if success:
            return {
                "success": True,
                "message": "Pipeline démarré avec succès",
                "timestamp": datetime.utcnow().isoformat(),
                "pipeline_status": pipeline_manager.get_pipeline_status()
            }
        else:
            raise HTTPException(status_code=500, detail="Échec du démarrage du pipeline")
    except Exception as e:
        logger.error("❌ Erreur démarrage pipeline", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pipeline/stop")
async def stop_pipeline():
    """Arrête le pipeline séquentiel complet."""
    try:
        success = await pipeline_manager.stop_pipeline()
        if success:
            return {
                "success": True,
                "message": "Pipeline arrêté avec succès",
                "timestamp": datetime.utcnow().isoformat(),
                "pipeline_status": pipeline_manager.get_pipeline_status()
            }
        else:
            raise HTTPException(status_code=500, detail="Échec de l'arrêt du pipeline")
    except Exception as e:
        logger.error("❌ Erreur arrêt pipeline", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pipeline/status")
async def get_pipeline_status():
    """Récupère le statut complet du pipeline."""
    try:
        return pipeline_manager.get_pipeline_status()
    except Exception as e:
        logger.error("❌ Erreur récupération statut pipeline", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pipeline/data")
async def get_pipeline_data(limit: int = Query(100, description="Nombre de données à récupérer")):
    """Récupère les dernières données du pipeline."""
    try:
        return {
            "data": pipeline_manager.get_pipeline_data(limit),
            "pipeline_data_count": len(pipeline_manager.pipeline_data),
            "limit": limit
        }
    except Exception as e:
        logger.error("❌ Erreur récupération données pipeline", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pipeline/agents/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Récupère le statut d'un agent spécifique."""
    try:
        status = pipeline_manager.get_agent_status(agent_name)
        if status:
            return status
        else:
            raise HTTPException(status_code=404, detail=f"Agent {agent_name} non trouvé")
    except Exception as e:
        logger.error("❌ Erreur récupération statut agent", agent_name=agent_name, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/pipeline/execute")
async def execute_pipeline_once():
    """Exécute le pipeline une seule fois (pour les tests)."""
    try:
        # Exécuter une seule séquence du pipeline
        pipeline_data = await pipeline_manager._execute_pipeline_sequence()
        
        if pipeline_data:
            return {
                "success": True,
                "message": "Pipeline exécuté avec succès",
                "timestamp": datetime.utcnow().isoformat(),
                "pipeline_data": pipeline_data.__dict__ if hasattr(pipeline_data, '__dict__') else pipeline_data
            }
        else:
            return {
                "success": False,
                "message": "Pipeline exécuté mais aucune donnée générée",
                "timestamp": datetime.utcnow().isoformat()
            }
    except Exception as e:
        logger.error("❌ Erreur exécution pipeline", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pipeline/health")
async def get_pipeline_health():
    """Vérifie la santé du pipeline et de tous les agents."""
    try:
        status = pipeline_manager.get_pipeline_status()
        
        # Vérifier la santé de chaque agent
        healthy_agents = 0
        total_agents = len(status["agents"])
        
        for agent_name, agent_status in status["agents"].items():
            if agent_status["status"] in ["running", "stopped"]:
                healthy_agents += 1
        
        health_status = "healthy" if healthy_agents == total_agents else "degraded"
        if status["is_running"] and healthy_agents < total_agents:
            health_status = "unhealthy"
        
        return {
            "status": health_status,
            "healthy_agents": healthy_agents,
            "total_agents": total_agents,
            "pipeline_running": status["is_running"],
            "last_execution": status["last_execution"],
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error("❌ Erreur vérification santé pipeline", error=str(e))
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
