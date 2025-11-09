"""
Session-aware logging utility for multi-user chat system.
Automatically includes session_id and timestamp in all log messages.
"""
import logging
from datetime import datetime
from typing import Optional


class SessionLogger:
    """
    Logger wrapper that automatically includes session context.
    
    Usage:
        logger = SessionLogger(__name__)
        logger.info(session_id, "Processing message")
        # Output: [session_abc123] [14:23:45] Processing message
    """
    
    def __init__(self, logger_name: str):
        """
        Initialize session logger.
        
        Args:
            logger_name: Name of the logger (typically __name__)
        """
        self.logger = logging.getLogger(logger_name)
    
    def _format_msg(self, session_id: Optional[str], msg: str) -> str:
        """
        Format message with session context and timestamp.
        
        Args:
            session_id: Session identifier (or None for global logs)
            msg: Log message
            
        Returns:
            Formatted message with [session_id] [timestamp] prefix
        """
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # Include milliseconds
        
        if session_id:
            return f"[{session_id}] [{timestamp}] {msg}"
        else:
            return f"[GLOBAL] [{timestamp}] {msg}"
    
    def info(self, session_id: Optional[str], msg: str):
        """Log info message with session context"""
        self.logger.info(self._format_msg(session_id, msg))
    
    def debug(self, session_id: Optional[str], msg: str):
        """Log debug message with session context"""
        self.logger.debug(self._format_msg(session_id, msg))
    
    def warning(self, session_id: Optional[str], msg: str):
        """Log warning message with session context"""
        self.logger.warning(self._format_msg(session_id, msg))
    
    def error(self, session_id: Optional[str], msg: str):
        """Log error message with session context"""
        self.logger.error(self._format_msg(session_id, msg))
    
    def exception(self, session_id: Optional[str], msg: str):
        """Log exception with session context and stack trace"""
        self.logger.exception(self._format_msg(session_id, msg))
    
    # Convenience methods for backward compatibility with standard logger
    def log_info(self, msg: str):
        """Log info without session context (for global messages)"""
        self.info(None, msg)
    
    def log_error(self, msg: str):
        """Log error without session context (for global messages)"""
        self.error(None, msg)
