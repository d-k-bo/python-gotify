import platform
import shutil
import subprocess
from io import BytesIO
from pathlib import Path
from time import sleep

import httpx
import pytest


@pytest.fixture(scope="module")
def run_test_server():
    test_server_dir = Path(__file__).parent / "test-server"

    system = platform.system().lower()
    try:
        arch = {
            "i386": "386",
            "x86_64": "amd64",
            "armv7l": "arm-7",
            "aarch64": "arm64",
        }[platform.machine()]
    except KeyError as err:
        raise Exception(
            f"Your architecture '{platform.machine()}' seems to be unsupported"
            "by gotify-server. If this assumption is incorrect, "
            "please create an issue on github."
        ) from err

    if system == "windows":
        gotify_binary = f"gotify-windows-{arch}.exe"
    elif system == "linux":
        gotify_binary = f"gotify-linux-{arch}"
    else:
        raise Exception(
            f"Your operating system '{system}' seems to be unsupported"
            "by gotify-server. If this assumption is incorrect, "
            "please create an issue on github."
        )

    gotify_binary_path = test_server_dir / gotify_binary

    if not gotify_binary_path.exists():
        import zipfile

        r = httpx.get(
            "https://github.com/gotify/server/releases/latest",
            follow_redirects=True,
        )
        tag_name = r.url.path.split("/")[-1]

        r = httpx.get(
            "https://github.com/gotify/server/releases/download/"
            f"{tag_name}/{gotify_binary}.zip",
            follow_redirects=True,
        )
        r.raise_for_status()

        zipfile.ZipFile(BytesIO(r.content)).extractall(test_server_dir)
        if system == "linux":
            subprocess.run(["chmod", "+x", str(gotify_binary_path)])

    (test_server_dir / "data").mkdir(exist_ok=True)
    shutil.copyfile(
        test_server_dir / "gotify.db", test_server_dir / "data" / "gotify.db"
    )
    with (test_server_dir / "gotify.log").open("wb") as logfile:
        p = subprocess.Popen(
            gotify_binary_path,
            cwd=test_server_dir,
            env={"GOTIFY_SERVER_PORT": "30080"},
            stdout=logfile,
        )
        # retry until server is reachable
        while True:
            try:
                r = httpx.get("http://localhost:30080")
            except httpx.ConnectError:
                sleep(0.1)
            else:
                break
        try:
            yield
        finally:
            p.kill()
