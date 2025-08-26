"""
Dremio Client - Python utilities for working with Dremio data sources.

This package provides tools for connecting to Dremio, querying data,
caching results, and working with metadata.
"""

from .dremio_client import (
    # Core connection
    DremioConnector,
    
    # Caching
    DremioCacheManager,
    default_cache_manager,
    
    query_dremio
)

# Export commonly used components
__all__ = [
    'DremioConnector',
    'DremioCacheManager',
    'default_cache_manager',
    'query_dremio'
]