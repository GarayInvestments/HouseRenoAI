"""
Memory Manager for AI Chat Sessions

Provides lightweight in-memory storage with TTL-based expiration
for maintaining conversational context across chat interactions.
"""
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MemoryManager:
    """
    In-memory storage for chat session context with automatic expiration.
    
    Features:
    - Session-based storage (keyed by session_id)
    - TTL (Time To Live) expiration (default: 10 minutes)
    - Automatic cleanup of expired sessions
    - Thread-safe operations
    
    Use cases:
    - Store last viewed client/project/permit IDs
    - Remember last action performed
    - Maintain conversation context
    - Track user preferences during session
    """
    
    def __init__(self, default_ttl_minutes: int = 10):
        """
        Initialize the memory manager.
        
        Args:
            default_ttl_minutes: Default time-to-live for stored values (minutes)
        """
        self._storage: Dict[str, Dict[str, Any]] = {}
        self._timestamps: Dict[str, float] = {}
        self.default_ttl = timedelta(minutes=default_ttl_minutes)
        logger.info(f"MemoryManager initialized with {default_ttl_minutes} minute TTL")
    
    def set(self, session_id: str, key: str, value: Any, ttl_minutes: Optional[int] = None) -> None:
        """
        Store a value in session memory.
        
        Args:
            session_id: Unique session identifier
            key: Key to store the value under
            value: Value to store (any JSON-serializable type)
            ttl_minutes: Optional custom TTL in minutes (overrides default)
        
        Example:
            memory.set("user-123", "last_client_id", "C-001")
            memory.set("user-123", "last_action", "viewed_project", ttl_minutes=5)
        """
        # Clean expired sessions first
        self._cleanup_expired()
        
        # Initialize session storage if doesn't exist
        if session_id not in self._storage:
            self._storage[session_id] = {}
            logger.debug(f"Created new session: {session_id}")
        
        # Store value
        self._storage[session_id][key] = value
        
        # Update timestamp
        ttl = timedelta(minutes=ttl_minutes) if ttl_minutes else self.default_ttl
        self._timestamps[session_id] = time.time() + ttl.total_seconds()
        
        logger.debug(f"Set {session_id}.{key} = {value} (expires in {ttl.total_seconds()}s)")
    
    def get(self, session_id: str, key: str, default: Any = None) -> Any:
        """
        Retrieve a value from session memory.
        
        Args:
            session_id: Unique session identifier
            key: Key to retrieve
            default: Default value if key not found or session expired
        
        Returns:
            Stored value or default if not found/expired
        
        Example:
            client_id = memory.get("user-123", "last_client_id")
            action = memory.get("user-123", "last_action", default="none")
        """
        # Clean expired sessions first
        self._cleanup_expired()
        
        # Check if session exists and hasn't expired
        if session_id not in self._storage:
            logger.debug(f"Session not found: {session_id}")
            return default
        
        if session_id not in self._timestamps or time.time() > self._timestamps[session_id]:
            logger.debug(f"Session expired: {session_id}")
            self._remove_session(session_id)
            return default
        
        # Retrieve value
        value = self._storage[session_id].get(key, default)
        logger.debug(f"Retrieved {session_id}.{key} = {value}")
        return value
    
    def get_all(self, session_id: str) -> Dict[str, Any]:
        """
        Get all stored values for a session.
        
        Args:
            session_id: Unique session identifier
        
        Returns:
            Dictionary of all key-value pairs for the session
        
        Example:
            context = memory.get_all("user-123")
            # Returns: {"last_client_id": "C-001", "last_action": "viewed_project"}
        """
        self._cleanup_expired()
        
        if session_id not in self._storage:
            return {}
        
        if session_id not in self._timestamps or time.time() > self._timestamps[session_id]:
            self._remove_session(session_id)
            return {}
        
        return self._storage[session_id].copy()
    
    def clear(self, session_id: str) -> None:
        """
        Clear all data for a specific session.
        
        Args:
            session_id: Unique session identifier
        
        Example:
            memory.clear("user-123")
        """
        if session_id in self._storage:
            self._remove_session(session_id)
            logger.info(f"Cleared session: {session_id}")
    
    def clear_all(self) -> None:
        """
        Clear all sessions (useful for testing or maintenance).
        
        Example:
            memory.clear_all()
        """
        count = len(self._storage)
        self._storage.clear()
        self._timestamps.clear()
        logger.info(f"Cleared all sessions ({count} total)")
    
    def exists(self, session_id: str, key: Optional[str] = None) -> bool:
        """
        Check if a session or specific key exists and hasn't expired.
        
        Args:
            session_id: Unique session identifier
            key: Optional specific key to check
        
        Returns:
            True if session/key exists and hasn't expired
        
        Example:
            if memory.exists("user-123", "last_client_id"):
                client_id = memory.get("user-123", "last_client_id")
        """
        self._cleanup_expired()
        
        if session_id not in self._storage:
            return False
        
        if session_id not in self._timestamps or time.time() > self._timestamps[session_id]:
            self._remove_session(session_id)
            return False
        
        if key is not None:
            return key in self._storage[session_id]
        
        return True
    
    def extend_ttl(self, session_id: str, additional_minutes: int = 10) -> bool:
        """
        Extend the TTL for a session.
        
        Args:
            session_id: Unique session identifier
            additional_minutes: Minutes to add to current expiration
        
        Returns:
            True if extended, False if session doesn't exist
        
        Example:
            memory.extend_ttl("user-123", 15)  # Add 15 more minutes
        """
        if session_id not in self._timestamps:
            return False
        
        current_expiry = self._timestamps[session_id]
        new_expiry = current_expiry + timedelta(minutes=additional_minutes).total_seconds()
        self._timestamps[session_id] = new_expiry
        
        logger.debug(f"Extended TTL for {session_id} by {additional_minutes} minutes")
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about current memory usage.
        
        Returns:
            Dictionary with stats (active_sessions, total_keys, oldest_session_age)
        
        Example:
            stats = memory.get_stats()
            # Returns: {"active_sessions": 3, "total_keys": 12, "oldest_session_age": 480}
        """
        self._cleanup_expired()
        
        total_keys = sum(len(session_data) for session_data in self._storage.values())
        
        oldest_age = 0
        if self._timestamps:
            current_time = time.time()
            oldest_timestamp = min(self._timestamps.values())
            oldest_age = int(current_time - (oldest_timestamp - self.default_ttl.total_seconds()))
        
        return {
            "active_sessions": len(self._storage),
            "total_keys": total_keys,
            "oldest_session_age_seconds": oldest_age,
            "default_ttl_minutes": self.default_ttl.total_seconds() / 60
        }
    
    def list_sessions(self) -> list[Dict[str, Any]]:
        """
        List all active sessions with their metadata.
        
        Returns:
            List of session information dictionaries
        
        Example:
            sessions = memory.list_sessions()
            # Returns: [{"session_id": "user-123", "keys": ["last_client_id"], "expires_in": 480}]
        """
        self._cleanup_expired()
        
        sessions = []
        current_time = time.time()
        
        for session_id in self._storage.keys():
            expiry_time = self._timestamps.get(session_id, current_time)
            expires_in = max(0, int(expiry_time - current_time))
            
            session_data = self._storage[session_id]
            metadata = session_data.get("metadata", {})
            
            sessions.append({
                "session_id": session_id,
                "metadata": metadata,
                "expires_in_seconds": expires_in,
                "key_count": len(session_data),
                "created_at": metadata.get("created_at", "unknown")
            })
        
        # Sort by created_at descending (newest first)
        sessions.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return sessions
    
    def _cleanup_expired(self) -> None:
        """Remove expired sessions from storage."""
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, expiry_time in self._timestamps.items()
            if current_time > expiry_time
        ]
        
        for session_id in expired_sessions:
            self._remove_session(session_id)
            logger.debug(f"Removed expired session: {session_id}")
    
    def _remove_session(self, session_id: str) -> None:
        """Remove a session and its timestamp."""
        self._storage.pop(session_id, None)
        self._timestamps.pop(session_id, None)


# Global memory manager instance
memory_manager = MemoryManager(default_ttl_minutes=10)
