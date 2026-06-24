"""Environment-backed application settings.

Configuration is read through small helpers instead of scattered direct
``os.environ`` access. That keeps defaults visible and makes configuration
behavior easy to test without starting Docker or MongoDB.
"""

import os
from typing import Mapping, Optional


DEFAULT_MONGODB_URI = "mongodb://mongodb:27017"
DEFAULT_MONGODB_DATABASE = "air-pollution"


def get_env(name: str, default: str, environ: Optional[Mapping[str, str]] = None) -> str:
    """Return a non-empty environment value or the provided default."""
    environ = environ or os.environ
    value = environ.get(name)
    return value if value else default


def get_mongodb_config(environ: Optional[Mapping[str, str]] = None):
    """Build the MongoDB config dictionary expected by the legacy adapter."""
    return {
        "uri": get_env("DB_URI", DEFAULT_MONGODB_URI, environ),
        "database": get_env("DB_NAME", DEFAULT_MONGODB_DATABASE, environ),
    }
