"""Error classes for gotify."""
import httpx

from .response_types import Error

__all__ = ["GotifyError", "GotifyConfigurationError"]


class GotifyError(Exception):
    """Raised if gotify serves an error response."""

    def __init__(self, response: httpx.Response) -> None:
        """Raise if gotify serves an error response.

        Args:
            response (requests.Response): The response object returned by the
                requests library.
        """
        self.response = response
        self.error: Error = self.response.json()

    def __str__(self) -> str:
        """Parse json error into string."""
        json = self.error
        if json.get("errorDescription") == "page not found":
            return (
                f'{json.get("errorCode")} {json.get("error")}: '
                f"{self.response.request.url}"
            )
        return (
            f'{json.get("errorCode")} {json.get("error")}: '
            f'{json.get("errorDescription")}'
        )


class GotifyConfigurationError(Exception):
    """Raised if the server URL or a required token is missing."""

    pass
