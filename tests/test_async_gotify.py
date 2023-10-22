import asyncio
from copy import deepcopy
from pathlib import Path
from typing import Any, List

import pytest
from typeguard import check_type

from gotify import AsyncGotify, GotifyConfigurationError, GotifyError
from gotify.response_types import (
    Application,
    Client,
    Health,
    Message,
    PagedMessages,
    User,
    VersionInfo,
)

agf = AsyncGotify()

BASE_URL = "http://localhost:30080"
APP_TOKEN = "AGo8b9paHo5wPkI"
CLIENT_TOKEN = "C4er8DTiNk08mtt"


@pytest.mark.usefixtures("run_test_server")
class TestAsyncGotify:
    data: dict[str, Any] = {}

    async def test_missing_url(self):
        with pytest.raises(GotifyConfigurationError) as exc_info:
            await agf.get_health()
        assert "base_url" in str(exc_info.value)
        agf.config(base_url=BASE_URL)

    async def test_missing_app_token(self):
        with pytest.raises(GotifyConfigurationError) as exc_info:
            await agf.create_message("foobar")
        assert "app_token" in str(exc_info.value)
        agf.config(app_token=APP_TOKEN)

    async def test_missing_client_token(self):
        with pytest.raises(GotifyConfigurationError) as exc_info:
            await agf.get_health()
        assert "client_token" in str(exc_info.value)
        agf.config(client_token=CLIENT_TOKEN)

    async def test_bad_auth_mode(self):
        with pytest.raises(GotifyConfigurationError) as exc_info:
            await agf._request(url_endpoint="/foobar", auth_mode="foobar")
        assert "authentification mode" in str(exc_info.value)

    async def test_bad_request(self):
        with pytest.raises(GotifyError) as exc_info:
            await agf._request(url_endpoint="/foobar")
        assert "Not Found" in str(exc_info.value)

        with pytest.raises(GotifyError) as exc_info:
            await agf._request(
                url_endpoint="/application", data={"foo": "bar"}, method="post"
            )
        assert "Bad Request" in str(exc_info.value)

    async def test_get_application(self):
        r = await agf.get_applications()
        check_type(r, List[Application])

    async def test_create_application(self):
        r1 = await agf.create_application("TestApplication")
        check_type(deepcopy(r1), Application)
        assert r1["name"] == "TestApplication"
        assert r1["description"] == ""

        r2 = await agf.create_application(
            "TestApplication2",
            "TestDescription",
            default_priority=4,
        )
        check_type(r2, Application)
        assert r2["name"] == "TestApplication2"
        assert r2["description"] == "TestDescription", r2
        assert r2["defaultPriority"] == 4

        self.data["app-id"] = r1["id"]
        self.data["default-image"] = r1["image"]

    async def test_update_application(self):
        r = await agf.update_application(
            self.data["app-id"],
            "UpdatedTestApplication",
            "UpdatedDescription",
            default_priority=6,
        )
        check_type(r, Application)
        assert r["name"] == "UpdatedTestApplication"
        assert r["description"] == "UpdatedDescription"
        assert r["defaultPriority"] == 6

    async def test_upload_application_image(self):
        with (Path(__file__).parent / "img.png").open("rb") as f:
            r = await agf.upload_application_image(self.data["app-id"], f)
        check_type(r, Application)
        assert r["image"] != self.data["default-image"]

    async def test_get_messages(self):
        r1 = await agf.get_messages(self.data["app-id"])
        check_type(r1, PagedMessages)

        r2 = await agf.get_messages()
        check_type(r2, PagedMessages)
        assert all((msg in r2["messages"] for msg in r1["messages"]))

    async def test_create_message(self):
        r1 = await agf.create_message("TestMessage1")
        check_type(r1, Message)
        assert r1["message"] == "TestMessage1"

        r2 = await agf.create_message("TestMessage2", priority=4, title="TestTitle")
        check_type(r2, Message)
        assert r2["message"] == "TestMessage2"
        assert r2.get("title") == "TestTitle"

        self.data["msg-id"] = r1["id"]

    async def test_delete_message(self):
        r = await agf.delete_message(self.data["msg-id"])
        assert r is None

    async def test_delete_messages(self):
        r1 = await agf.delete_messages(self.data["app-id"])
        assert r1 is None

        r2 = await agf.get_messages(self.data["app-id"])
        check_type(r2, PagedMessages)
        assert len(r2["messages"]) == 0

        r3 = await agf.delete_messages()
        assert r3 is None

        r4 = await agf.get_messages()
        check_type(r4, PagedMessages)
        assert len(r4["messages"]) == 0

    async def test_delete_application(self):
        r = await agf.delete_application(self.data["app-id"])
        assert r is None

    async def test_get_clients(self):
        r = await agf.get_clients()
        check_type(r, List[Client])

    async def test_create_client(self):
        r = await agf.create_client("TestClient")
        check_type(r, Client)
        assert r["name"] == "TestClient"
        self.data["client-id"] = r["id"]

    async def test_update_client(self):
        r = await agf.update_client(self.data["client-id"], "UpdatedTestClient")
        check_type(r, Client)
        assert r["name"] == "UpdatedTestClient"

    async def test_delete_client(self):
        r = await agf.delete_client(self.data["client-id"])
        assert r is None

    async def test_get_current_user(self):
        r = await agf.get_current_user()
        check_type(r, User)

    async def test_set_password(self):
        r = await agf.set_password("admin")
        assert r is None

    async def test_get_users(self):
        r = await agf.get_users()
        check_type(r, List[User])

    async def test_create_user(self):
        r1 = await agf.create_user("TestUser1", "TestPassword")
        check_type(r1, User)
        assert r1["name"] == "TestUser1"

        r2 = await agf.create_user("TestUser2", "TestPassword", admin=True)
        check_type(r2, User)
        assert r2["name"] == "TestUser2"
        assert r2.get("admin") is True

        self.data["user-id"] = r1["id"]

    async def test_get_user(self):
        r1 = await agf.get_user(self.data["user-id"])
        check_type(r1, User)
        assert r1["name"] == "TestUser1"

    async def test_update_user(self):
        r1 = await agf.update_user(self.data["user-id"], "UpdatedTestUser1")
        check_type(r1, User)
        assert r1["name"] == "UpdatedTestUser1"

        r2 = await agf.update_user(
            self.data["user-id"],
            name="UpdatedUpdatedTestUser1",
            passwd="UpdatedTestPasword",  # changes can't be tested
            admin=True,
        )
        check_type(r2, User)
        assert r2["name"] == "UpdatedUpdatedTestUser1"
        assert r2.get("admin") is True

    async def test_delete_user(self):
        r = await agf.delete_user(self.data["user-id"])
        assert r is None

    async def test_get_health(self):
        r = await agf.get_health()
        check_type(r, Health)

    # TODO
    # async def test_get_plugins(self):
    #     pass

    # async def test_get_plugin_config(self):
    #     pass

    # async def test_update_plugin_config(self):
    #     pass

    # async def test_disable_plugin(self):
    #     pass

    # async def test_get_plugin_display(self):
    #     pass

    # async def test_enable_plugin(self):
    #     pass

    async def test_get_version(self):
        r = await agf.get_version()
        check_type(r, VersionInfo)

    async def test_stream(self):
        n = 5

        async def send():
            async with AsyncGotify(BASE_URL, app_token=APP_TOKEN) as app_gf:
                for i in range(n):
                    await app_gf.create_message(f"msg-{i}")

        async def recv():
            client_gf = AsyncGotify(BASE_URL, client_token=CLIENT_TOKEN)
            i = 0
            async for msg in (agen := client_gf.stream()):
                assert msg["message"] == f"msg-{i}"
                if i == n - 1:
                    break
                i += 1
            # pytest-asyncio doesn't clean up async generators
            # should not be required when using `asyncio.run()`
            # expected to be fixed with
            # https://github.com/pytest-dev/pytest-asyncio/issues/235
            await agen.aclose()

        await asyncio.gather(recv(), send())
