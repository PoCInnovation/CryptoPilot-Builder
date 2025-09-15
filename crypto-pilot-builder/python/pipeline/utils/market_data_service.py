#!/usr/bin/env python3
"""
Service unifié pour les données de marché
Combine CoinGecko (prix) et Alchemy (blockchain)
"""

import aiohttp
import asyncio
import structlog
from typing import Dict, Any, Optional, List
from datetime import datetime
import os

logger = structlog.get_logger(__name__)

class MarketDataService:
    """Service unifié pour les données de marché."""
    
    def __init__(self):
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        self.session = None
        
        # Cache pour éviter trop d'appels API
        self.price_cache = {}
        self.cache_duration = 30  # secondes
        
    async def get_session(self):
        """Crée une session aiohttp si nécessaire."""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=10),
                headers={"User-Agent": "TradingBot/1.0"}
            )
        return self.session
    
    async def get_crypto_price(self, coin_id: str) -> Optional[float]:
        """Récupère le prix d'une crypto via CoinGecko."""
        try:
            session = await self.get_session()
            
            # Vérifier le cache
            cache_key = f"price_{coin_id}"
            if cache_key in self.price_cache:
                cached_data = self.price_cache[cache_key]
                if (datetime.now() - cached_data["timestamp"]).seconds < self.cache_duration:
                    logger.info("Prix récupéré du cache", coin=coin_id, price=cached_data["price"])
                    return cached_data["price"]
            
            url = f"{self.coingecko_base_url}/simple/price"
            params = {"ids": coin_id, "vs_currencies": "usd"}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    price = data.get(coin_id, {}).get("usd")
                    
                    if price:
                        # Mettre en cache
                        self.price_cache[cache_key] = {
                            "price": price,
                            "timestamp": datetime.now()
                        }
                        
                        logger.info("Prix temps réel récupéré", 
                                  coin=coin_id, price=price, source="CoinGecko")
                        return price
                    else:
                        logger.warning("Prix non trouvé", coin=coin_id)
                        return None
                else:
                    logger.error("Erreur API CoinGecko", 
                               coin=coin_id, status=response.status)
                    return None
                    
        except Exception as e:
            logger.error("Erreur récupération prix", coin=coin_id, error=str(e))
            return None
    

    
    async def get_complete_market_data(self, coin_id: str) -> Dict[str, Any]:
        """Récupère les données de prix crypto."""
        try:
            # Récupérer le prix crypto
            price = await self.get_crypto_price(coin_id)
            
            if price:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "crypto": {
                        "id": coin_id,
                        "price_usd": price,
                        "source": "CoinGecko"
                    },
                    "success": True
                }
            else:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "crypto": {"id": coin_id, "price_usd": None, "source": None},
                    "success": False,
                    "error": "Impossible de récupérer le prix crypto"
                }
                
        except Exception as e:
            logger.error("Erreur récupération données crypto", error=str(e))
            return {
                "timestamp": datetime.now().isoformat(),
                "crypto": {"id": coin_id, "price_usd": None, "source": None},
                "success": False,
                "error": str(e)
            }
    
    async def get_multiple_prices(self, coin_ids: List[str]) -> Dict[str, float]:
        """Récupère les prix de plusieurs cryptos."""
        try:
            session = await self.get_session()
            
            url = f"{self.coingecko_base_url}/simple/price"
            params = {"ids": ",".join(coin_ids), "vs_currencies": "usd"}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    prices = {}
                    
                    for coin_id in coin_ids:
                        price = data.get(coin_id, {}).get("usd")
                        if price:
                            prices[coin_id] = price
                            # Mettre en cache
                            cache_key = f"price_{coin_id}"
                            self.price_cache[cache_key] = {
                                "price": price,
                                "timestamp": datetime.now()
                            }
                    
                    logger.info("Prix multiples récupérés", 
                              coins=list(prices.keys()), count=len(prices))
                    return prices
                else:
                    logger.error("Erreur API CoinGecko multiple", status=response.status)
                    return {}
                    
        except Exception as e:
            logger.error("Erreur récupération prix multiples", error=str(e))
            return {}
    
    async def close(self):
        """Ferme la session aiohttp."""
        if self.session:
            await self.session.close()
            self.session = None

# Instance globale
market_data_service = MarketDataService()
