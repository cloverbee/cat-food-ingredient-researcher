"""
Rate limiting utilities for FastAPI using slowapi.

This module provides rate limiting functionality to protect API endpoints
from abuse, especially expensive operations like LLM-based search.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

# Create a global limiter instance
# The limiter will be initialized in main.py and stored in app.state
limiter = Limiter(key_func=get_remote_address)
