"""Access your gotify server."""

from __future__ import annotations

__version__ = "0.5"


from .async_gotify import AsyncGotify
from .errors import GotifyConfigurationError, GotifyError
from .gotify import Gotify

__all__ = ["AsyncGotify", "Gotify", "GotifyError", "GotifyConfigurationError"]
