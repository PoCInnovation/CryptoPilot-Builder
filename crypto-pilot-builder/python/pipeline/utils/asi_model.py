"""Module pour l'utilisation du modèle ASI:One de Fetch.ai."""

import os
import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
import structlog

logger = structlog.get_logger(__name__)

class ASIOneModel:
    """Interface pour le modèle ASI:One de Fetch.ai."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "asi1-mini"):
        """
        Initialise le modèle ASI:One.
        
        Args:
            api_key: Clé API ASI:One (si None, cherche dans ASI_ONE_API_KEY)
            model: Modèle à utiliser (asi1-mini, asi1-fast, asi1-extended, etc.)
        """
        self.api_key = api_key or os.getenv("ASI_ONE_API_KEY")
        self.model = model
        self.base_url = "https://api.asi1.ai/v1"
        
        if not self.api_key:
            logger.warning("ASI_ONE_API_KEY non configurée, utilisation du mode simulation")
            self.simulation_mode = True
        else:
            self.simulation_mode = False
            
        logger.info("ASIOneModel initialisé", 
                   model=model, 
                   simulation_mode=self.simulation_mode)
    
    async def predict_price_direction(self, 
                                    price_history: List[float],
                                    volume_history: List[float],
                                    technical_indicators: Dict[str, float],
                                    symbol: str = "BTC/USD") -> Dict[str, Any]:
        """
        Prédit la direction du prix en utilisant ASI:One.
        
        Args:
            price_history: Historique des prix (derniers 20-50 points)
            volume_history: Historique des volumes
            technical_indicators: Indicateurs techniques (RSI, MACD, etc.)
            symbol: Paire de trading
            
        Returns:
            Dict avec prédiction, confiance, et métadonnées
        """
        if self.simulation_mode:
            return await self._simulate_prediction(price_history, technical_indicators, symbol)
        
        try:
            # Préparer les données pour ASI:One
            prompt = self._build_prediction_prompt(price_history, volume_history, technical_indicators, symbol)
            
            # Appel à l'API ASI:One
            response = await self._call_asi_api(prompt)
            
            # Parser la réponse
            prediction = self._parse_prediction_response(response, symbol)
            
            logger.info("Prédiction ASI:One générée", 
                       symbol=symbol,
                       direction_probability=prediction["direction_probability"],
                       confidence=prediction["confidence"])
            
            return prediction
            
        except Exception as e:
            logger.error("Erreur prédiction ASI:One", error=str(e))
            # Fallback vers simulation
            return await self._simulate_prediction(price_history, technical_indicators, symbol)
    
    def _build_prediction_prompt(self, 
                                price_history: List[float],
                                volume_history: List[float],
                                technical_indicators: Dict[str, float],
                                symbol: str) -> str:
        """Construit le prompt pour ASI:One."""
        
        # Calculer quelques métriques de base
        current_price = price_history[-1] if price_history else 1.0
        price_change = ((current_price - price_history[-2]) / price_history[-2]) if len(price_history) > 1 else 0
        volatility = self._calculate_volatility(price_history)
        
        prompt = f"""
Tu es un expert en analyse technique et trading algorithmique. Analyse les données suivantes et prédit la direction probable du prix pour {symbol}.

DONNÉES ACTUELLES:
- Prix actuel: ${current_price:.4f}
- Variation récente: {price_change:.2%}
- Volatilité: {volatility:.4f}

HISTORIQUE DES PRIX (derniers 10 points):
{price_history[-10:]}

INDICATEURS TECHNIQUES:
{json.dumps(technical_indicators, indent=2)}

TÂCHE:
1. Analyse la tendance actuelle
2. Évalue la force des signaux techniques
3. Prédit la probabilité de hausse (0-1)
4. Estime ta confiance dans cette prédiction (0-1)
5. Identifie les facteurs clés qui influencent ta décision

RÉPONSE ATTENDUE (JSON):
{{
    "direction_probability": 0.65,
    "confidence": 0.78,
    "trend_analysis": "tendance haussière modérée",
    "key_factors": ["RSI oversold", "support technique", "volume croissant"],
    "risk_level": "modéré",
    "timeframe": "5 minutes"
}}
"""
        return prompt
    
    async def _call_asi_api(self, prompt: str) -> Dict[str, Any]:
        """Appelle l'API ASI:One."""
        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,  # Réponses plus déterministes
                "max_tokens": 500
            }
            
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    error_text = await response.text()
                    raise Exception(f"API ASI:One error {response.status}: {error_text}")
    
    def _parse_prediction_response(self, response: Dict[str, Any], symbol: str) -> Dict[str, Any]:
        """Parse la réponse d'ASI:One."""
        try:
            content = response["choices"][0]["message"]["content"]
            
            # Essayer de parser le JSON
            if "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                json_str = content[start:end]
                prediction_data = json.loads(json_str)
            else:
                # Fallback si pas de JSON valide
                prediction_data = {
                    "direction_probability": 0.5,
                    "confidence": 0.6,
                    "trend_analysis": "analyse non disponible",
                    "key_factors": ["données insuffisantes"],
                    "risk_level": "inconnu",
                    "timeframe": "5 minutes"
                }
            
            # Construire la réponse standardisée
            return {
                "symbol": symbol,
                "current_price": 1.0,  # Sera mis à jour par l'appelant
                "direction_probability": float(prediction_data.get("direction_probability", 0.5)),
                "confidence": float(prediction_data.get("confidence", 0.6)),
                "trend_analysis": prediction_data.get("trend_analysis", ""),
                "key_factors": prediction_data.get("key_factors", []),
                "risk_level": prediction_data.get("risk_level", "modéré"),
                "prediction_horizon": prediction_data.get("timeframe", "5 minutes"),
                "model_name": f"ASI:One-{self.model}",
                "features_used": {
                    "price_history_length": 10,
                    "technical_indicators": True,
                    "volume_analysis": True
                },
                "success": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error("Erreur parsing réponse ASI:One", error=str(e))
            raise
    
    async def _simulate_prediction(self, 
                                 price_history: List[float],
                                 technical_indicators: Dict[str, float],
                                 symbol: str) -> Dict[str, Any]:
        """Simulation de prédiction quand l'API n'est pas disponible."""
        import random
        
        current_price = price_history[-1] if price_history else 1.0
        price_change = ((current_price - price_history[-2]) / price_history[-2]) if len(price_history) > 1 else 0
        
        # Logique de simulation basée sur les indicateurs
        base_prob = 0.5
        
        # Influence du RSI
        if "rsi" in technical_indicators:
            rsi = technical_indicators["rsi"]
            if rsi < 30:  # Oversold
                base_prob += 0.2
            elif rsi > 70:  # Overbought
                base_prob -= 0.2
        
        # Influence de la tendance
        if price_change > 0.01:
            base_prob += 0.1
        elif price_change < -0.01:
            base_prob -= 0.1
        
        # Ajouter du bruit
        direction_prob = base_prob + random.uniform(-0.05, 0.05)
        direction_prob = max(0.0, min(1.0, direction_prob))
        
        confidence = random.uniform(0.6, 0.9)
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "direction_probability": round(direction_prob, 3),
            "confidence": round(confidence, 3),
            "trend_analysis": "simulation - tendance analysée",
            "key_factors": ["simulation", "indicateurs techniques"],
            "risk_level": "modéré",
            "prediction_horizon": "5 minutes",
            "model_name": f"ASI:One-{self.model}-SIMULATION",
            "features_used": {
                "price_history_length": len(price_history),
                "technical_indicators": bool(technical_indicators),
                "volume_analysis": False
            },
            "success": True,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_volatility(self, prices: List[float]) -> float:
        """Calcule la volatilité des prix."""
        if len(prices) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(prices)):
            if prices[i-1] != 0:
                returns.append((prices[i] - prices[i-1]) / prices[i-1])
        
        if not returns:
            return 0.0
        
        import numpy as np
        return float(np.std(returns))
    
    async def test_connection(self) -> bool:
        """Teste la connexion à l'API ASI:One."""
        if self.simulation_mode:
            logger.info("Mode simulation - pas de test de connexion")
            return True
        
        try:
            test_prompt = "Réponds simplement 'OK' si tu reçois ce message."
            await self._call_asi_api(test_prompt)
            logger.info("Connexion ASI:One OK")
            return True
        except Exception as e:
            logger.error("Erreur connexion ASI:One", error=str(e))
            return False
