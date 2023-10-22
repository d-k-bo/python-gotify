"""TypedDicts to describe JSON responses.

Based on https://gotify.net/api-docs?urls.primaryName=v2.4.0.
"""
from typing import Optional, TypedDict


class Application(TypedDict, total=False):
    description: str
    id: int
    image: str
    internal: bool
    name: str
    token: str
    defaultPriority: int
    lastUsed: Optional[str]


class Client(TypedDict, total=False):
    id: int
    name: str
    token: str
    lastUsed: Optional[str]


class Error(TypedDict, total=False):
    error: str
    errorCode: int
    errorDescription: str


class Health(TypedDict, total=False):
    database: str
    health: str


class Message(TypedDict, total=False):
    appid: int
    date: str
    extras: dict
    id: int
    message: str
    priority: int
    title: str


class PagedMessages(TypedDict, total=False):
    messages: list[Message]
    paging: "Paging"


class Paging(TypedDict, total=False):
    limit: int
    next: str
    since: int
    size: int


class PluginConf(TypedDict, total=False):
    author: str
    capabilities: list[str]
    enabled: bool
    id: int
    license: str
    modulePath: str
    name: str
    token: str
    website: str


class User(TypedDict, total=False):
    admin: bool
    id: int
    name: str


UserPass = TypedDict("UserPass", {"pass": str})

UserWithPass = TypedDict(
    "UserWithPass",
    {"admin": bool, "id": int, "name": str, "pass": str},
    total=False,
)


class VersionInfo(TypedDict, total=False):
    buildDate: str
    commit: str
    version: str
