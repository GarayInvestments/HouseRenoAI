"""
Security Sanitizer for Logging

Redacts sensitive information before logging to prevent credential leakage.
Protects JWT tokens, API keys, passwords, OAuth tokens, and other secrets.
"""

import re
from typing import Any, Dict, Union


# Patterns for sensitive data detection
SENSITIVE_PATTERNS = {
    'jwt_token': r'(eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]{10,})',
    'bearer_token': r'(Bearer\s+[a-zA-Z0-9_\-\.]{20,})',
    'api_key': r'([a-zA-Z0-9_-]{32,})',  # Common API key lengths
    'password': r'("password"\s*:\s*"[^"]+"|\'password\'\s*:\s*\'[^\']+\')',
    'client_secret': r'("client_secret"\s*:\s*"[^"]+"|\'client_secret\'\s*:\s*\'[^\']+\')',
    'access_token': r'("access_token"\s*:\s*"[^"]+"|\'access_token\'\s*:\s*\'[^\']+\')',
    'refresh_token': r'("refresh_token"\s*:\s*"[^"]+"|\'refresh_token\'\s*:\s*\'[^\']+\')',
    'authorization': r'("Authorization"\s*:\s*"[^"]+"|\'Authorization\'\s*:\s*\'[^\']+\')',
}

# Fields that should always be redacted in dicts
SENSITIVE_KEYS = {
    'password', 'pwd', 'passwd', 'secret', 'api_key', 'apikey', 
    'access_token', 'refresh_token', 'token', 'bearer',
    'authorization', 'auth', 'client_secret', 'private_key',
    'OPENAI_API_KEY', 'QUICKBOOKS_CLIENT_SECRET', 'JWT_SECRET_KEY'
}


def sanitize_string(text: str, redaction_text: str = '[REDACTED]') -> str:
    """
    Sanitize a string by redacting sensitive patterns.
    
    Args:
        text: String to sanitize
        redaction_text: Replacement text for redacted content
        
    Returns:
        Sanitized string with sensitive data redacted
    """
    if not isinstance(text, str):
        return text
    
    sanitized = text
    
    # Apply all sensitive patterns
    for pattern_name, pattern in SENSITIVE_PATTERNS.items():
        if pattern_name == 'jwt_token':
            # Special handling for JWT - show first/last 4 chars
            def jwt_replacer(match):
                token = match.group(1)
                if len(token) > 20:
                    return f"{token[:8]}...{token[-4:]}"
                return redaction_text
            sanitized = re.sub(pattern, jwt_replacer, sanitized, flags=re.IGNORECASE)
        else:
            sanitized = re.sub(pattern, redaction_text, sanitized, flags=re.IGNORECASE)
    
    return sanitized


def sanitize_dict(data: Dict[str, Any], redaction_text: str = '[REDACTED]') -> Dict[str, Any]:
    """
    Recursively sanitize a dictionary by redacting sensitive keys.
    
    Args:
        data: Dictionary to sanitize
        redaction_text: Replacement text for redacted content
        
    Returns:
        Sanitized dictionary with sensitive values redacted
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    
    for key, value in data.items():
        # Check if key is sensitive (case-insensitive)
        if any(sensitive_key.lower() in key.lower() for sensitive_key in SENSITIVE_KEYS):
            # Show first/last 4 chars for tokens, full redaction for passwords
            if 'password' in key.lower() or 'secret' in key.lower():
                sanitized[key] = redaction_text
            elif isinstance(value, str) and len(value) > 20:
                sanitized[key] = f"{value[:4]}...{value[-4:]}"
            else:
                sanitized[key] = redaction_text
        elif isinstance(value, dict):
            # Recursively sanitize nested dicts
            sanitized[key] = sanitize_dict(value, redaction_text)
        elif isinstance(value, list):
            # Sanitize lists
            sanitized[key] = [
                sanitize_dict(item, redaction_text) if isinstance(item, dict)
                else sanitize_string(item, redaction_text) if isinstance(item, str)
                else item
                for item in value
            ]
        elif isinstance(value, str):
            # Sanitize string values
            sanitized[key] = sanitize_string(value, redaction_text)
        else:
            sanitized[key] = value
    
    return sanitized


def sanitize_log_message(message: Union[str, Dict], redaction_text: str = '[REDACTED]') -> Union[str, Dict]:
    """
    Main sanitization function that handles both strings and dicts.
    
    Args:
        message: Log message to sanitize (string or dict)
        redaction_text: Replacement text for redacted content
        
    Returns:
        Sanitized message safe for logging
        
    Examples:
        >>> sanitize_log_message("Bearer eyJhbGciOiJIUzI1...")
        "Bearer [REDACTED]"
        
        >>> sanitize_log_message({"password": "secret123", "email": "user@example.com"})
        {"password": "[REDACTED]", "email": "user@example.com"}
    """
    if isinstance(message, dict):
        return sanitize_dict(message, redaction_text)
    elif isinstance(message, str):
        return sanitize_string(message, redaction_text)
    else:
        return message


def create_safe_logger(logger):
    """
    Wrap a logger to automatically sanitize all log messages.
    
    Args:
        logger: Logger instance to wrap
        
    Returns:
        Wrapped logger that sanitizes all messages
        
    Usage:
        >>> import logging
        >>> logger = logging.getLogger(__name__)
        >>> safe_logger = create_safe_logger(logger)
        >>> safe_logger.info("Token: eyJhbGci...")  # Automatically sanitized
    """
    class SafeLogger:
        def __init__(self, base_logger):
            self._logger = base_logger
        
        def _sanitize_args(self, *args):
            """Sanitize all arguments before logging"""
            return tuple(sanitize_log_message(arg) for arg in args)
        
        def debug(self, msg, *args, **kwargs):
            self._logger.debug(sanitize_log_message(msg), *self._sanitize_args(*args), **kwargs)
        
        def info(self, msg, *args, **kwargs):
            self._logger.info(sanitize_log_message(msg), *self._sanitize_args(*args), **kwargs)
        
        def warning(self, msg, *args, **kwargs):
            self._logger.warning(sanitize_log_message(msg), *self._sanitize_args(*args), **kwargs)
        
        def error(self, msg, *args, **kwargs):
            self._logger.error(sanitize_log_message(msg), *self._sanitize_args(*args), **kwargs)
        
        def critical(self, msg, *args, **kwargs):
            self._logger.critical(sanitize_log_message(msg), *self._sanitize_args(*args), **kwargs)
        
        # Delegate other attributes to base logger
        def __getattr__(self, name):
            return getattr(self._logger, name)
    
    return SafeLogger(logger)


if __name__ == '__main__':
    # Test examples
    print("Testing sanitizer...")
    
    # Test JWT token
    jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
    print(f"\nJWT: {sanitize_string(jwt)}")
    
    # Test dict with sensitive data
    data = {
        "email": "user@example.com",
        "password": "secret123",
        "access_token": "sk-proj-abc123def456",
        "client_name": "John Doe"
    }
    print(f"\nDict: {sanitize_dict(data)}")
    
    # Test Authorization header
    auth_header = 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
    print(f"\nAuth Header: {sanitize_string(auth_header)}")
