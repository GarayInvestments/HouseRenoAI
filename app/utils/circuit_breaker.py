"""
Circuit Breaker Pattern for QuickBooks API Resilience

Prevents cascading failures when QuickBooks API is experiencing issues.
After consecutive failures, circuit opens and requests fail fast without
attempting API calls. After cooldown period, circuit enters half-open state
to test recovery.

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Failing fast, no API calls attempted
- HALF_OPEN: Testing recovery with limited requests

Thresholds:
- Failure threshold: 3 consecutive failures → OPEN
- Cooldown periods: 30s → 60s → 120s (exponential backoff)
- Success threshold in HALF_OPEN: 1 success → CLOSED
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerError(Exception):
    """Raised when circuit is open and request is blocked"""
    pass


class CircuitBreaker:
    """
    Circuit breaker for protecting against cascading API failures.
    
    Usage:
        breaker = CircuitBreaker(name="quickbooks_api", failure_threshold=3)
        
        @breaker.call
        async def fetch_customers():
            return await qb_client.get_customers()
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 3,
        cooldown_seconds: int = 30,
        max_cooldown_seconds: int = 120
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.max_cooldown_seconds = max_cooldown_seconds
        
        # State tracking
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.opened_at: Optional[datetime] = None
        self.current_cooldown = cooldown_seconds
        
        logger.info(
            f"[CIRCUIT_BREAKER] Initialized '{name}' "
            f"(threshold: {failure_threshold}, cooldown: {cooldown_seconds}s)"
        )
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.state != CircuitState.OPEN:
            return False
        
        if not self.opened_at:
            return True
        
        elapsed = (datetime.utcnow() - self.opened_at).total_seconds()
        return elapsed >= self.current_cooldown
    
    def _record_success(self):
        """Record successful call"""
        if self.state == CircuitState.HALF_OPEN:
            # Success in half-open → close circuit
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.current_cooldown = self.cooldown_seconds
            logger.info(
                f"[CIRCUIT_BREAKER] '{self.name}' → CLOSED (recovery successful)"
            )
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            if self.failure_count > 0:
                logger.info(
                    f"[CIRCUIT_BREAKER] '{self.name}' reset failure count "
                    f"(was {self.failure_count})"
                )
                self.failure_count = 0
    
    def _record_failure(self, error: Exception):
        """Record failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failure in half-open → reopen circuit
            self.state = CircuitState.OPEN
            self.opened_at = datetime.utcnow()
            # Increase cooldown exponentially
            self.current_cooldown = min(
                self.current_cooldown * 2,
                self.max_cooldown_seconds
            )
            logger.warning(
                f"[CIRCUIT_BREAKER] '{self.name}' → OPEN (recovery failed, "
                f"cooldown: {self.current_cooldown}s, error: {error})"
            )
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                # Threshold reached → open circuit
                self.state = CircuitState.OPEN
                self.opened_at = datetime.utcnow()
                logger.error(
                    f"[CIRCUIT_BREAKER] '{self.name}' → OPEN "
                    f"({self.failure_count} consecutive failures, "
                    f"cooldown: {self.current_cooldown}s, last error: {error})"
                )
            else:
                logger.warning(
                    f"[CIRCUIT_BREAKER] '{self.name}' failure {self.failure_count}/"
                    f"{self.failure_threshold} (error: {error})"
                )
    
    def _check_state(self):
        """Check and update circuit state before call"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                # Cooldown elapsed → try half-open
                self.state = CircuitState.HALF_OPEN
                logger.info(
                    f"[CIRCUIT_BREAKER] '{self.name}' → HALF_OPEN "
                    f"(testing recovery after {self.current_cooldown}s)"
                )
            else:
                # Still cooling down
                elapsed = (datetime.utcnow() - self.opened_at).total_seconds()
                remaining = self.current_cooldown - elapsed
                raise CircuitBreakerError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Retry in {remaining:.0f}s. "
                    f"Last failure: {self.last_failure_time}"
                )
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        
        Args:
            func: Async function to call
            *args, **kwargs: Arguments to pass to function
            
        Returns:
            Function result if successful
            
        Raises:
            CircuitBreakerError: If circuit is open
            Exception: Original exception from function (circuit records failure)
        """
        self._check_state()
        
        try:
            result = await func(*args, **kwargs)
            self._record_success()
            return result
        except Exception as e:
            self._record_failure(e)
            raise
    
    def __call__(self, func: Callable):
        """Decorator for wrapping functions with circuit breaker"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        return wrapper
    
    def get_status(self) -> dict:
        """Get current circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "current_cooldown_seconds": self.current_cooldown,
            "last_failure_time": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "time_until_retry": (
                self.current_cooldown - (datetime.utcnow() - self.opened_at).total_seconds()
                if self.state == CircuitState.OPEN and self.opened_at
                else 0
            )
        }
    
    def reset(self):
        """Manually reset circuit breaker (for testing/admin)"""
        old_state = self.state
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.opened_at = None
        self.current_cooldown = self.cooldown_seconds
        logger.info(f"[CIRCUIT_BREAKER] '{self.name}' manually reset (was {old_state.value})")


# Global circuit breaker instance for QuickBooks API
qb_circuit_breaker = CircuitBreaker(
    name="quickbooks_api",
    failure_threshold=3,
    cooldown_seconds=30,
    max_cooldown_seconds=120
)
