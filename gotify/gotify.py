"""Synchronous implementation of the gotify client."""

from __future__ import annotations

from types import TracebackType
from typing import Any, BinaryIO, TypeVar

import httpx

from .errors import GotifyConfigurationError, GotifyError
from .response_types import (
    Application,
    Client,
    Health,
    Message,
    PagedMessages,
    PluginConf,
    User,
    VersionInfo,
)

__all__ = ["Gotify"]

GotifyType = TypeVar("GotifyType", bound="Gotify")


# --- Main Class ----------------------------------------------------


class Gotify:
    """Synchronous implementation of a Gotify client."""

    def __init__(
        self,
        base_url: str | None = None,
        app_token: str | None = None,
        client_token: str | None = None,
    ) -> None:
        """Initialise the Gotify object.

        Args:
            base_url (str, optional): Base URL of your Gotify instance,
                eg. https://gotify.example.com.

            app_token (str, optional): token to authenticate to receive
                messages and manage stuff.

            client_token (str, optional): token to authenticate to send
                messages.
        """
        self.base_url: str | None = base_url
        self.app_token: str | None = app_token
        self.client_token: str | None = client_token
        self.http_client: httpx.Client | None = None

    def config(
        self,
        base_url: str | None = None,
        app_token: str | None = None,
        client_token: str | None = None,
    ) -> None:
        """Set up the gotify object."""
        if base_url:
            self.base_url = base_url
        if app_token:
            self.app_token = app_token
        if client_token:
            self.client_token = client_token

    def __enter__(self: GotifyType) -> GotifyType:  # -> Self:
        if self.http_client is None:
            self.http_client = httpx.Client().__enter__()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_value: BaseException,
        traceback: TracebackType,
    ) -> None:
        if self.http_client is not None:
            self.http_client.__exit__(exc_type, exc_value, traceback)
            self.http_client = None

    # --- Applications -------------------------------------------------------

    def get_applications(self) -> list[Application]:
        """Return all applications."""
        return self._request("/application")

    def create_application(
        self,
        name: str,
        description: str | None = None,
    ) -> Application:
        """Create an application."""
        return self._request(
            "/application",
            data={"name": name, "description": description},
            method="post",
        )

    def update_application(
        self,
        id: int,
        name: str,
        description: str | None = None,
    ) -> Application:
        """Update an application."""
        return self._request(
            f"/application/{id}",
            data={"name": name, "description": description},
            method="put",
        )

    def delete_application(self, id: int) -> None:
        """Delete an application."""
        return self._request(f"/application/{id}", method="delete")

    def upload_application_image(self, id: int, image: BinaryIO) -> Application:
        """Upload an image for an application."""
        return self._request(f"/application/{id}/image", file=image, method="post")

    # --- Messages -----------------------------------------------------------

    def get_messages(
        self,
        app_id: int | None = None,
        limit: int | None = None,
        since: int | None = None,
    ) -> PagedMessages:
        """Return all messages, optionally from a specific application."""
        if app_id is None:
            return self._request("/message", data={"limit": limit, "since": since})
        else:
            return self._request(
                f"/application/{app_id}/message",
                data={"limit": limit, "since": since},
            )

    def create_message(
        self,
        message: str,
        extras: dict | None = None,
        priority: int | None = None,
        title: str | None = None,
    ) -> Message:
        """Create a message."""
        return self._request(
            "/message",
            data={
                "message": message,
                "extras": extras,
                "priority": priority,
                "title": title,
            },
            method="post",
            auth_mode="app",
        )

    def delete_messages(self, app_id: int | None = None) -> None:
        """Delete all messages, optionally from a specific application."""
        if app_id is None:
            return self._request("/message", method="delete")
        else:
            return self._request(f"/application/{app_id}/message", method="delete")

    def delete_message(self, msg_id: int) -> None:
        """Delete a message with an id."""
        return self._request(f"/message/{msg_id}", method="delete")

    # --- Clients -------------------------------------------------------------

    def get_clients(self) -> list[Client]:
        """Return all clients."""
        return self._request("/client")

    def create_client(self, name: str) -> Client:
        """Create a client."""
        return self._request("/client", data={"name": name}, method="post")

    def update_client(self, id: int, name: str) -> Client:
        """Update a client."""
        return self._request(f"/client/{id}", data={"name": name}, method="put")

    def delete_client(self, id: int) -> None:
        """Delete a client."""
        return self._request(f"/client/{id}", method="delete")

    # --- Users ---------------------------------------------------------------

    def get_current_user(self) -> User:
        """Return the current user."""
        return self._request("/current/user")

    def set_password(self, passwd: str) -> None:
        """Update the password of the current user."""
        return self._request(
            "/current/user/password",
            data={"pass": passwd},
            method="post",
        )

    def get_users(self) -> list[User]:
        """Return all users."""
        return self._request("/user")

    def create_user(self, name: str, passwd: str, admin: bool | None = None) -> User:
        """Create a user."""
        return self._request(
            "/user",
            data={"name": name, "pass": passwd, "admin": admin},
            method="post",
        )

    def get_user(self, id: int) -> User:
        """Get a user."""
        return self._request(f"/user/{id}")

    def update_user(
        self,
        id: int,
        name: str | None = None,
        passwd: str | None = None,
        admin: bool | None = None,
    ) -> User:
        """Update a user."""
        return self._request(
            f"/user/{id}",
            data={"name": name, "pass": passwd, "admin": admin},
            method="post",
        )

    def delete_user(self, id: int) -> None:
        """Delete a user."""
        return self._request(f"/user/{id}", method="delete")

    # --- Health --------------------------------------------------------------

    def get_health(self) -> Health:
        """Get health information."""
        return self._request("/health")

    # --- Plugins -------------------------------------------------------------

    def get_plugins(self) -> list[PluginConf]:
        """Return all plugins."""
        return self._request("/plugin")

    def get_plugin_config(self, id: int) -> PluginConf:
        """Get YAML configuration for Configurer plugin."""
        return self._request(f"/plugin/{id}/config")

    def update_plugin_config(self, id: int) -> None:
        """Update YAML configuration for Configurer plugin."""
        return self._request(f"/plugin/{id}/config", method="post")

    def disable_plugin(self, id: int) -> None:
        """Disable a plugin."""
        return self._request(f"/plugin/{id}/disable", method="post")

    def get_plugin_display(self, id: int) -> str:
        """Get display info for a Displayer plugin."""
        return self._request(f"/plugin/{id}/display")

    def enable_plugin(self, id: int) -> None:
        """Enable a plugin."""
        return self._request(f"/plugin/{id}/enable", method="post")

    # --- Version -------------------------------------------------------------

    def get_version(self) -> VersionInfo:
        """Get version information."""
        return self._request("/version")

    # --- Utils ---------------------------------------------------------------

    def _request(
        self,
        url_endpoint: str,
        data: dict[str, Any] | None = None,
        file: BinaryIO | None = None,
        method: str = "get",
        auth_mode: str = "client",
    ) -> Any:
        # if Gotify isn't used as a context manager
        if self.http_client is None:
            with self:
                return self._request(
                    url_endpoint=url_endpoint,
                    data=data,
                    file=file,
                    method=method,
                    auth_mode=auth_mode,
                )

        if data:
            # remove items that are None
            for key in [k for k, v in data.items() if v is None]:
                del data[key]

        r = self.http_client.request(
            method,
            self._get_url(url_endpoint),
            headers={"X-Gotify-Key": self._get_token(auth_mode)},
            params=data if method == "get" else None,
            json=data if method != "get" else None,
            files={"file": file} if file is not None else {},
        )
        if r.is_success:
            try:
                return r.json()
            except ValueError:
                return r.text if r.text else None
        else:
            raise GotifyError(r)

    def _get_url(self, url_endpoint: str) -> str:
        if not self.base_url:
            raise GotifyConfigurationError(
                "'base_url' is not defined. You need to set it up before "
                "accessing your Gotify server. It should be something like "
                "'https://gotify.example.com/'"
            )
        return self.base_url.strip("/") + "/" + url_endpoint.strip("/")

    def _get_token(self, auth_mode: str) -> str:
        if auth_mode.lower() == "client":
            if not self.client_token:
                raise GotifyConfigurationError(
                    "'client_token' is not defined. You need to set it up"
                    "before accessing client functions."
                )
            return self.client_token
        elif auth_mode.lower() == "app":
            if not self.app_token:
                raise GotifyConfigurationError(
                    "'app_token' is not defined. You need to set it up before "
                    "sending messages."
                )
            return self.app_token
        raise GotifyConfigurationError(f"Unknown authentification mode '{auth_mode}'.")
