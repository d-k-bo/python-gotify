"""Access your gotify server."""

__version__ = "0.3"

from io import IOBase
from typing import Optional, Union

import requests

# --- Main Class ----------------------------------------------------


class gotify:
    """The gotify class."""

    def __init__(self, base_url=None, app_token=None, client_token=None):
        """Initialise."""
        self.base_url = None
        self.app_token = None
        self.client_token = None
        self.config(base_url, app_token, client_token)

    def config(
        self,
        base_url: str = None,
        app_token: str = None,
        client_token: str = None,
    ):
        """Set up the gotify module.

        Args:
            base_url (str): Base URL of your Gotify instance,
                eg. https://gotify.example.com.

            app_token (str): token to authenticate to receive messages
                and manage stuff.

            client_token (str): token to authenticate to send messages.
        """
        if base_url:
            self.base_url = base_url
        if app_token:
            self.app_token = app_token
        if client_token:
            self.client_token = client_token

    # --- Applications -------------------------------------------------------

    def get_applications(self):
        """Get list of applications."""
        return self._request("/application")

    def create_application(
        self,
        name: str,
        description: str = None,
    ):
        """Create a new application."""
        data = {"name": name}
        if description is not None:
            data["description"] = description
        return self._request("/application", data, method="post")

    def update_application(
        self,
        id: int,
        name: str,
        description: str = None,
    ):
        """Update an application."""
        data = {"name": name}
        if description is not None:
            data["description"] = description
        return self._request(f"/application/{id}", data, method="put")

    def delete_application(self, id: int):
        """Remove an application."""
        return self._request(f"/application/{id}", method="delete")

    def upload_application_image(self, id: int, image: IOBase):
        """Upload an image for an application."""
        return self._request(f"/application/{id}/image", image, method="post")

    # --- Messages -----------------------------------------------------------

    def get_messages(
        self, app_id: int = None, limit: int = None, since: int = None
    ):
        """Retreive messages."""
        data = {}
        if limit is not None:
            data["limit"] = limit
        if since is not None:
            data["since"] = since

        if app_id is None:
            return self._request("/message", data)
        else:
            return self._request(f"/application/{app_id}/message", data)

    def create_message(
        self,
        message: str,
        extras: Optional[dict] = None,
        priority: Optional[int] = None,
        title: Optional[str] = None,
    ):
        """Send a message."""
        data = {"message": message}
        if extras is not None:
            data["extras"] = extras
        if priority is not None:
            data["priority"] = priority
        if title is not None:
            data["title"] = title

        return self._request("/message", data, method="post", auth_mode="app")

    def delete_messages(self, app_id: int = None):
        """Delete messages for one or all applications."""
        if app_id is None:
            return self._request("/message", method="delete")
        else:
            return self._request(
                f"/application/{app_id}/message", method="delete"
            )

    def delete_message(self, msg_id: int):
        """Delete a specific message."""
        return self._request(f"/message/{msg_id}", method="delete")

    # --- Clients -------------------------------------------------------------

    def get_clients(self):
        """Get list of clients."""
        return self._request("/client")

    def create_client(self, name: str):
        """Create a new client."""
        return self._request("/client", {"name": name}, method="post")

    def update_client(self, id: int, name: str):
        """Update a client."""
        return self._request(f"/client/{id}", {"name": name}, method="put")

    def delete_client(self, id: int):
        """Delete a client."""
        return self._request(f"/client/{id}", method="delete")

    # --- Users ---------------------------------------------------------------

    def get_current_user(self):
        """Get details of current user."""
        return self._request("/current/user")

    def set_password(self, passwd: str):
        """Set password for current user."""
        return self._request(
            "/current/user/password",
            {"pass": passwd},
            method="post",
        )

    def get_users(self):
        """Get list of users."""
        return self._request("/user")

    def create_user(self, name: str, passwd: str, admin: bool = None):
        """Create new user."""
        data = {"name": name, "pass": passwd}
        if admin is not None:
            data["admin"] = admin
        return self._request("/user", data, method="post")

    def get_user(self, id: int):
        """Get details of a user."""
        return self._request(f"/user/{id}")

    def update_user(
        self,
        id: int,
        name: str = None,
        passwd: str = None,
        admin: bool = None,
    ):
        """Update a user."""
        data = {}
        if name is not None:
            data["name"] = name
        if passwd is not None:
            data["passwd"] = passwd
        if admin is not None:
            data["admin"] = admin
        return self._request(f"/user/{id}", data, method="post")

    def delete_user(self, id: int):
        """Delete a user."""
        return self._request(f"/user/{id}", method="delete")

    # --- Health --------------------------------------------------------------

    def get_health(self):
        """Get server status."""
        return self._request("/health")

    # --- Plugins -------------------------------------------------------------

    def get_plugins(self):
        """Get list of plugins."""
        return self._request("/plugin")

    def get_plugin_config(self, id: int):
        """Get config for a Configurer plugin."""
        return self._request(f"/plugin/{id}/config")

    def update_plugin_config(self, id: int):
        """Update config for a Configurer plugin."""
        return self._request(f"/plugin/{id}/config", method="post")

    def disable_plugin(self, id: int):
        """Disable a plugin."""
        return self._request(f"/plugin/{id}/disable", method="post")

    def get_plugin_display(self, id: int):
        """Get details for a Displayer plugin."""
        return self._request(f"/plugin/{id}/display")

    def enable_plugin(self, id: int):
        """Enable a plugin."""
        return self._request(f"/plugin/{id}/enable", method="post")

    # --- Version -------------------------------------------------------------

    def get_version(self):
        """Get server version."""
        return self._request("/version")

    # --- Utils ---------------------------------------------------------------

    def _request(
        self,
        url: str,
        *args: Optional[Union[dict, IOBase]],
        method: str = "get",
        auth_mode: str = "client",
    ) -> Union[dict, list, str]:
        if not self.base_url:
            raise GotifyConfigurationError(
                "'base_url' is not defined. You need to set it up before "
                "accessing your Gotify server. It should be something like "
                "'https://gotify.example.com/'"
            )
        kwargs = {}
        for arg in args:
            if isinstance(arg, dict):
                if method == "get":
                    kwargs["params"] = arg
                else:
                    kwargs["json"] = arg
            elif isinstance(arg, IOBase):
                kwargs["files"] = {"file": arg}

        r = requests.request(
            method,
            self._join_urls(self.base_url, url),
            headers={"X-Gotify-Key": self._get_token(auth_mode)},
            **kwargs,
        )
        if r.status_code == requests.codes.OK:
            try:
                return r.json()
            except ValueError:
                return r.text
        else:
            raise GotifyError(r)

    def _join_urls(self, base_url: str, relative_url: str):
        return base_url.strip("/") + "/" + relative_url.strip("/")

    def _get_token(self, auth_mode: str):
        if auth_mode.lower() == "client":
            if not self.client_token:
                raise GotifyConfigurationError(
                    "'Client Token' is not defined. You need to set it up"
                    "before accessing client functions."
                )
            return self.client_token
        elif auth_mode.lower() == "app":
            if not self.app_token:
                raise GotifyConfigurationError(
                    "'App Token' is not defined. You need to set it up before "
                    "sending messages."
                )
            return self.app_token


# --- Exceptions ----------------------------------------------------------


class GotifyError(Exception):
    """Error class."""

    def __init__(self, response: requests.Response):
        """Initialise."""
        self.response = response

    def __str__(self):
        """Parse json error into string."""
        json = self.response.json()
        if json["errorDescription"] == "page not found":
            return (
                f'{json["errorCode"]} {json["error"]}: '
                f"{self.response.request.url}"
            )
        return (
            f'{json["errorCode"]} {json["error"]}: '
            f'{json["errorDescription"]}'
        )


class GotifyConfigurationError(Exception):
    """Config Error Class."""

    pass


# --- Support legacy functions ------------------------------------------------

_gotify_obj = gotify()

config = _gotify_obj.config
get_applications = _gotify_obj.get_applications
create_application = _gotify_obj.create_application
update_application = _gotify_obj.update_application
delete_application = _gotify_obj.delete_application
upload_application_image = _gotify_obj.upload_application_image
get_messages = _gotify_obj.get_messages
create_message = _gotify_obj.create_message
delete_messages = _gotify_obj.delete_messages
delete_message = _gotify_obj.delete_message
get_clients = _gotify_obj.get_clients
create_client = _gotify_obj.create_client
update_client = _gotify_obj.update_client
delete_client = _gotify_obj.delete_client
get_current_user = _gotify_obj.get_current_user
set_password = _gotify_obj.set_password
get_users = _gotify_obj.get_users
create_user = _gotify_obj.create_user
get_user = _gotify_obj.get_user
update_user = _gotify_obj.update_user
delete_user = _gotify_obj.delete_user
get_health = _gotify_obj.get_health
get_plugins = _gotify_obj.get_plugins
get_plugin_config = _gotify_obj.get_plugin_config
update_plugin_config = _gotify_obj.update_plugin_config
disable_plugin = _gotify_obj.disable_plugin
get_plugin_display = _gotify_obj.get_plugin_display
enable_plugin = _gotify_obj.enable_plugin
get_version = _gotify_obj.get_version
