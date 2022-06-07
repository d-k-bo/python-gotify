from copy import deepcopy
from pathlib import Path
from typing import Any, List

import pytest
from trycast import trycast  # type: ignore[import]

from gotify import Gotify, GotifyConfigurationError, GotifyError
from gotify.response_types import (
    Application,
    Client,
    Health,
    Message,
    PagedMessages,
    User,
    VersionInfo,
)

gf = Gotify()

BASE_URL = "http://localhost:30080"
APP_TOKEN = "AGo8b9paHo5wPkI"
CLIENT_TOKEN = "C4er8DTiNk08mtt"


@pytest.mark.usefixtures("run_test_server")
class TestGotify:
    data: dict[str, Any] = {}

    def test_missing_url(self):
        with pytest.raises(GotifyConfigurationError) as exc_info:
            gf.get_health()
        assert "base_url" in str(exc_info.value)
        gf.config(base_url=BASE_URL)

    def test_missing_app_token(self):
        with pytest.raises(GotifyConfigurationError) as exc_info:
            gf.create_message("foobar")
        assert "app_token" in str(exc_info.value)
        gf.config(app_token=APP_TOKEN)

    def test_missing_client_token(self):
        with pytest.raises(GotifyConfigurationError) as exc_info:
            gf.get_health()
        assert "client_token" in str(exc_info.value)
        gf.config(client_token=CLIENT_TOKEN)

    def test_bad_auth_mode(self):
        with pytest.raises(GotifyConfigurationError) as exc_info:
            gf._request(url_endpoint="/foobar", auth_mode="foobar")
        assert "authentification mode" in str(exc_info.value)

    def test_bad_request(self):
        with pytest.raises(GotifyError) as exc_info:
            gf._request(url_endpoint="/foobar")
        assert "Not Found" in str(exc_info.value)

        with pytest.raises(GotifyError) as exc_info:
            gf._request(url_endpoint="/application", data={"foo": "bar"}, method="post")
        assert "Bad Request" in str(exc_info.value)

    def test_get_application(self):
        r = gf.get_applications()
        assert trycast(List[Application], r) is not None

    def test_create_application(self):
        r1 = gf.create_application("TestApplication")
        assert trycast(Application, deepcopy(r1)) is not None
        assert r1["name"] == "TestApplication"
        assert r1["description"] == ""

        r2 = gf.create_application("TestApplication2", "TestDescription")
        assert trycast(Application, r2) is not None
        assert r2["name"] == "TestApplication2"
        assert r2["description"] == "TestDescription", r2

        self.data["app-id"] = r1["id"]
        self.data["default-image"] = r1["image"]

    def test_update_application(self):
        r = gf.update_application(
            self.data["app-id"], "UpdatedTestApplication", "UpdatedDescription"
        )
        assert trycast(Application, r) is not None
        assert r["name"] == "UpdatedTestApplication"
        assert r["description"] == "UpdatedDescription"

    def test_upload_application_image(self):
        with (Path(__file__).parent / "img.png").open("rb") as f:
            r = gf.upload_application_image(self.data["app-id"], f)
        assert trycast(Application, r) is not None
        assert r["image"] != self.data["default-image"]

    def test_get_messages(self):
        r1 = gf.get_messages(self.data["app-id"])
        assert trycast(PagedMessages, r1) is not None

        r2 = gf.get_messages()
        assert trycast(PagedMessages, r2) is not None, r2
        assert all((msg in r2["messages"] for msg in r1["messages"]))

    def test_create_message(self):
        r1 = gf.create_message("TestMessage1")
        assert trycast(Message, r1) is not None
        assert r1["message"] == "TestMessage1"

        r2 = gf.create_message("TestMessage2", priority=4, title="TestTitle")
        assert trycast(Message, r2) is not None
        assert r2["message"] == "TestMessage2"
        assert r2.get("title") == "TestTitle"

        self.data["msg-id"] = r1["id"]

    def test_delete_message(self):
        r = gf.delete_message(self.data["msg-id"])
        assert r is None

    def test_delete_messages(self):
        r1 = gf.delete_messages(self.data["app-id"])
        assert r1 is None

        r2 = gf.get_messages(self.data["app-id"])
        assert trycast(PagedMessages, r2) is not None
        assert len(r2["messages"]) == 0

        r3 = gf.delete_messages()
        assert r3 is None

        r4 = gf.get_messages()
        assert trycast(PagedMessages, r4) is not None
        assert len(r4["messages"]) == 0

    def test_delete_application(self):
        r = gf.delete_application(self.data["app-id"])
        assert r is None

    def test_get_clients(self):
        r = gf.get_clients()
        assert trycast(List[Client], r) is not None

    def test_create_client(self):
        r = gf.create_client("TestClient")
        assert trycast(Client, r) is not None
        assert r["name"] == "TestClient"
        self.data["client-id"] = r["id"]

    def test_update_client(self):
        r = gf.update_client(self.data["client-id"], "UpdatedTestClient")
        assert trycast(Client, r) is not None
        assert r["name"] == "UpdatedTestClient"

    def test_delete_client(self):
        r = gf.delete_client(self.data["client-id"])
        assert r is None

    def test_get_current_user(self):
        r = gf.get_current_user()
        assert trycast(User, r) is not None

    def test_set_password(self):
        r = gf.set_password("admin")
        assert r is None

    def test_get_users(self):
        r = gf.get_users()
        assert trycast(List[User], r) is not None

    def test_create_user(self):
        r1 = gf.create_user("TestUser1", "TestPassword")
        assert trycast(User, r1) is not None
        assert r1["name"] == "TestUser1"

        r2 = gf.create_user("TestUser2", "TestPassword", admin=True)
        assert trycast(User, r2) is not None
        assert r2["name"] == "TestUser2"
        assert r2.get("admin") is True

        self.data["user-id"] = r1["id"]

    def test_get_user(self):
        r1 = gf.get_user(self.data["user-id"])
        assert trycast(User, r1) is not None
        assert r1["name"] == "TestUser1"

    def test_update_user(self):
        r1 = gf.update_user(self.data["user-id"], "UpdatedTestUser1")
        assert trycast(User, r1) is not None
        assert r1["name"] == "UpdatedTestUser1"

        r2 = gf.update_user(
            self.data["user-id"],
            name="UpdatedUpdatedTestUser1",
            passwd="UpdatedTestPasword",  # changes can't be tested
            admin=True,
        )
        assert trycast(User, r2) is not None
        assert r2["name"] == "UpdatedUpdatedTestUser1"
        assert r2.get("admin") is True

    def test_delete_user(self):
        r = gf.delete_user(self.data["user-id"])
        assert r is None

    def test_get_health(self):
        r = gf.get_health()
        assert trycast(Health, r) is not None

    # TODO
    # def test_get_plugins(self):
    #     pass

    # def test_get_plugin_config(self):
    #     pass

    # def test_update_plugin_config(self):
    #     pass

    # def test_disable_plugin(self):
    #     pass

    # def test_get_plugin_display(self):
    #     pass

    # def test_enable_plugin(self):
    #     pass

    def test_get_version(self):
        r = gf.get_version()
        assert trycast(VersionInfo, r) is not None
