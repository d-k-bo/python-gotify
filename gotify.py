"""Access your gotify server"""

__version__ = "0.1"

from io import IOBase
from typing import Optional, Union

import requests


# --- Module Configuration ----------------------------------------------------


BASE_URL = ""
APP_TOKEN = ""
CLIENT_TOKEN = ""


def config(base_url: str, app_token: str, client_token: str):
    """Set up the gotify module

    Args:
        base_url (str): Base URL of your Gotify instance,
            eg. https://gotify.example.com.

        app_token (str): token to authentificate to receive messages
            and manage stuff.

        client_token (str): token to authentificate to send messages.
    """
    if base_url:
        global BASE_URL
        BASE_URL = base_url
    if app_token:
        global APP_TOKEN
        APP_TOKEN = app_token
    if client_token:
        global CLIENT_TOKEN
        CLIENT_TOKEN = client_token


# --- Applications ------------------------------------------------------------


def get_applications():
    return _request("/application")


def create_application(
    name: str,
    description: str = None,
    id: int = None,
    image: str = None,
    internal: bool = None,
    token: str = None,
):
    data = {"name": name}
    if description is not None:
        data["description"] = description
    if id is not None:
        data["id"] = id
    if image is not None:
        data["image"] = image
    if internal is not None:
        data["internal"] = internal
    if token is not None:
        data["token"] = token
    return _request("/application", data, method="post")


def update_application(
    id: int,
    name: str,
    description: str = None,
    image: str = None,
    internal: bool = None,
    token: str = None,
):
    data = {"name": name}
    if description is not None:
        data["description"] = description
    if image is not None:
        data["image"] = image
    if internal is not None:
        data["internal"] = internal
    if token is not None:
        data["token"] = token
    return _request(f"/application/{id}", data, method="put")


def delete_application(id: int):
    return _request(f"/application/{id}", method="delete")


def upload_application_image(id: int, image: IOBase):
    return _request(f"/application/{id}/image", image, method="post")


# --- Messages ----------------------------------------------------------------


def get_messages(app_id: int = None, limit: int = None, since: int = None):
    data = {}
    if limit is not None:
        data["limit"] = limit
    if since is not None:
        data["since"] = since

    if app_id is None:
        return _request("/message", data)
    else:
        return _request(f"/application/{app_id}/message", data)


def create_message(
    message: str,
    appid: Optional[int] = None,
    date: Optional[str] = None,
    extras: Optional[dict] = None,
    id: Optional[int] = None,
    priority: Optional[int] = None,
    title: Optional[int] = None,
):
    data = {"message": message}
    if appid is not None:
        data["appid"] = appid
    if date is not None:
        data["date"] = date
    if extras is not None:
        data["extras"] = extras
    if id is not None:
        data["id"] = id
    if priority is not None:
        data["priority"] = priority
    if title is not None:
        data["title"] = title

    return _request("/message", data, method="post", auth_mode="app")


def delete_messages(app_id: int = None):
    if app_id is None:
        return _request("/message", method="delete")
    else:
        _request("client", f"/application/{app_id}/message", method="delete")


def delete_message(msg_id: int):
    return _request(f"/message/{msg_id}", method="delete")


# --- Clients -----------------------------------------------------------------


def get_clients():
    return _request("/client")


def create_client(
    name: str,
    description: str = None,
    id: int = None,
    token: str = None,
):
    data = {"name": name}
    if description is not None:
        data["description"] = description
    if id is not None:
        data["id"] = id
    if token is not None:
        data["token"] = token
    return _request("/client", data, method="post")


def update_client(
    id: int,
    name: str,
    description: str = None,
    token: str = None,
):
    data = {"name": name}
    if description is not None:
        data["description"] = description
    if token is not None:
        data["token"] = token
    return _request(f"/client/{id}", data, method="put")


def delete_client(id: int):
    return _request(f"/client/{id}", method="delete")


# --- Users -------------------------------------------------------------------


def get_current_user():
    return _request("/current/user")


def set_password(passwd: str):
    return _request(
        "client",
        "/current/user",
        {"pass": passwd},
        method="post",
    )


def get_users():
    return _request("/user")


def create_user(name: str, passwd: str, admin: bool = None):
    data = {"name": name, "pass": passwd}
    if admin is not None:
        data["admin"] = admin
    return _request("/user", data, method="post")


def get_user(id: int):
    return _request(f"/user/{id}")


def update_user(
    id: int,
    name: str = None,
    passwd: str = None,
    admin: bool = None,
):
    data = {}
    if name is not None:
        data["name"] = name
    if passwd is not None:
        data["passwd"] = passwd
    if admin is not None:
        data["admin"] = admin
    return _request(f"/user/{id}", data, method="post")


def delete_user(id: int):
    return _request(f"/user/{id}", method="delete")


# --- Health ------------------------------------------------------------------


def get_health():
    return _request("/health")


# --- Plugins -----------------------------------------------------------------


def get_plugins():
    return _request("/plugin")


def get_plugin_config(id: int):
    return _request(f"/plugin/{id}/config")


def update_plugin_config(id: int):
    return _request(f"/plugin/{id}/config", method="post")


def disable_plugin(id: int):
    return _request(f"/plugin/{id}/disable", method="post")


def get_plugin_display(id: int):
    return _request(f"/plugin/{id}/display")


def enable_plugin(id: int):
    return _request(f"/plugin/{id}/enable", method="post")


# --- Version -----------------------------------------------------------------


def get_version():
    return _request("/version")


# --- Utils -------------------------------------------------------------------


def _request(
    url: str,
    *args: Optional[Union[dict, IOBase]],
    method: str = "get",
    auth_mode: str = "client",
) -> Union[dict, list, str]:
    if not BASE_URL:
        raise GotifyConfigurationError(
            "'BASE_URL' is not defined. You need to set it up before "
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
        _join_urls(BASE_URL, url),
        headers={"X-Gotify-Key": _get_token(auth_mode)},
        **kwargs,
    )
    if r.status_code == requests.codes.OK:
        try:
            return r.json()
        except ValueError:
            return r.text
    else:
        raise GotifyError(r)


def _join_urls(base_url: str, relative_url: str):
    return base_url.strip("/") + "/" + relative_url.strip("/")


def _get_token(auth_mode: str):
    if auth_mode.lower() == "client":
        if not CLIENT_TOKEN:
            raise GotifyConfigurationError(
                "'CLIENT_TOKEN' is not defined. You need to set it up before "
                "accessing client functions."
            )
        return CLIENT_TOKEN
    elif auth_mode.lower() == "app":
        if not APP_TOKEN:
            raise GotifyConfigurationError(
                "'APP_TOKEN' is not defined. You need to set it up before "
                "sending messages."
            )
        return APP_TOKEN


# --- Exceptions --------------------------------------------------------------


class GotifyError(Exception):
    def __init__(self, response: requests.Response):
        self.response = response

    def __str__(self):
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
    pass
