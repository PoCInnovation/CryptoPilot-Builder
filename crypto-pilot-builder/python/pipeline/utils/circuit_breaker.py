"""Circuit Breaker pattern pour la gestion des erreurs."""

import time
import functools
from typing import Callable, Any, Optional
import structlog

logger = structlog.get_logger(__name__)

class CircuitBreaker:
    """Circuit Breaker pattern pour gérer les erreurs d'API."""
    
    def __init__(self, fail_max: int = 5, reset_timeout: int = 60):
        self.fail_max = fail_max
        self.reset_timeout = reset_timeout
        self.fail_count = 0
        self.last_fail_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def __call__(self, func: Callable) -> Callable:
        """Décorateur pour appliquer le circuit breaker."""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            return await self._call(func, *args, **kwargs)
        return wrapper
    
    async def _call(self, func: Callable, *args, **kwargs) -> Any:
        """Exécute la fonction avec le circuit breaker."""
        if self.state == "OPEN":
            if time.time() - self.last_fail_time > self.reset_timeout:
                logger.info("Circuit breaker: passage en HALF_OPEN")
                self.state = "HALF_OPEN"
            else:
                logger.warning("Circuit breaker: circuit OPEN, requête rejetée")
                raise Exception("Circuit breaker OPEN")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Appelé quand la fonction réussit."""
        if self.state == "HALF_OPEN":
            logger.info("Circuit breaker: retour en CLOSED")
            self.state = "CLOSED"
        self.fail_count = 0
    
    def _on_failure(self):
        """Appelé quand la fonction échoue."""
        self.fail_count += 1
        self.last_fail_time = time.time()
        
        if self.fail_count >= self.fail_max:
            logger.error("Circuit breaker: passage en OPEN", 
                        fail_count=self.fail_count,
                        reset_timeout=self.reset_timeout)
            self.state = "OPEN"
        else:
            logger.warning("Circuit breaker: échec", 
                         fail_count=self.fail_count,
                         max_fails=self.fail_max)
    
    def get_state(self) -> str:
        """Retourne l'état actuel du circuit breaker."""
        return self.state
    
    def reset(self):
        """Reset manuel du circuit breaker."""
        self.state = "CLOSED"
        self.fail_count = 0
        self.last_fail_time = 0
        logger.info("Circuit breaker: reset manuel")
