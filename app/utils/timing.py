"""
Performance timing utilities for monitoring operation durations.
"""
import time
import logging
from functools import wraps
from typing import Optional, Callable, Any

logger = logging.getLogger(__name__)


def log_timing(session_id: Optional[str], operation: str, duration: float):
    """
    Log operation timing for performance analysis.
    
    Args:
        session_id: Session identifier (or None for global operations)
        operation: Name of the operation being timed
        duration: Duration in seconds
    """
    session_prefix = f"[{session_id}]" if session_id else "[GLOBAL]"
    logger.info(f"{session_prefix} [TIMING] {operation} took {duration:.3f}s")


class OperationTimer:
    """
    Context manager for timing operations.
    
    Usage:
        with OperationTimer(session_id, "context_build") as timer:
            # ... do work ...
            pass
        # Automatically logs timing on exit
    """
    
    def __init__(self, session_id: Optional[str], operation: str):
        """
        Initialize timer.
        
        Args:
            session_id: Session identifier
            operation: Name of operation being timed
        """
        self.session_id = session_id
        self.operation = operation
        self.start_time = None
        self.duration = None
    
    def __enter__(self):
        """Start timing"""
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and log result"""
        self.duration = time.time() - self.start_time
        log_timing(self.session_id, self.operation, self.duration)
        return False  # Don't suppress exceptions


def timed_operation(operation_name: str):
    """
    Decorator for timing function execution.
    
    Usage:
        @timed_operation("fetch_data")
        async def fetch_data(session_id: str):
            # ... implementation ...
            pass
    
    Note: Assumes first argument is session_id
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to extract session_id from first arg
            session_id = args[0] if args else kwargs.get('session_id')
            
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                log_timing(session_id, operation_name, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_timing(session_id, f"{operation_name}_FAILED", duration)
                raise
        
        return wrapper
    return decorator


class RequestTimer:
    """
    Timer for tracking multiple operations within a request.
    
    Usage:
        timer = RequestTimer(session_id)
        timer.start("context_build")
        # ... build context ...
        timer.stop("context_build")
        
        timer.start("openai_call")
        # ... call OpenAI ...
        timer.stop("openai_call")
        
        # Get summary
        summary = timer.get_summary()
        # {'context_build': 0.823, 'openai_call': 1.942, 'total': 2.765}
    """
    
    def __init__(self, session_id: Optional[str]):
        """
        Initialize request timer.
        
        Args:
            session_id: Session identifier
        """
        self.session_id = session_id
        self.timings = {}
        self.active_timers = {}
        self.request_start = time.time()
    
    def start(self, operation: str):
        """
        Start timing an operation.
        
        Args:
            operation: Name of operation to time
        """
        self.active_timers[operation] = time.time()
    
    def stop(self, operation: str):
        """
        Stop timing an operation and record duration.
        
        Args:
            operation: Name of operation to stop
        """
        if operation in self.active_timers:
            duration = time.time() - self.active_timers[operation]
            self.timings[operation] = duration
            del self.active_timers[operation]
            log_timing(self.session_id, operation, duration)
    
    def get_summary(self) -> dict:
        """
        Get summary of all timings.
        
        Returns:
            Dict with operation names as keys and durations as values,
            plus 'total' key with total request time
        """
        total_time = time.time() - self.request_start
        return {
            **self.timings,
            'total': total_time
        }
    
    def log_summary(self):
        """Log complete timing summary"""
        summary = self.get_summary()
        session_prefix = f"[{self.session_id}]" if self.session_id else "[GLOBAL]"
        
        # Format summary as key=value pairs
        summary_str = " | ".join([f"{k}={v:.3f}s" for k, v in summary.items()])
        logger.info(f"{session_prefix} [TIMING SUMMARY] {summary_str}")
