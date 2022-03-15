import platform
import shutil
import subprocess
from io import BytesIO
from pathlib import Path

import nox


@nox.session
def format(session: nox.Session):
    session.install("black", "isort")
    session.run("isort", ".")
    session.run("black", ".")


@nox.session
def lint(session: nox.Session):
    session.install(
        "flakeheaven",
        "flake8-docstrings",
        "flake8-annotations",
    )
    session.run("flakeheaven", "lint")


@nox.session
def mypy(session: nox.Session) -> None:
    session.install(".", "mypy", "types-requests", "nox", "pytest")
    session.run("mypy", ".")


@nox.session(python=["3.9", "3.10"])
def test(session: nox.Session):
    session.install(
        ".",
        "coverage",
        "pytest",
        "trycast",
    )

    test_server_dir = Path(__file__).parent / "tests" / "test-server"

    system = platform.system().lower()
    try:
        arch = {
            "i386": "386",
            "x86_64": "amd64",
            "armv7l": "arm-7",
            "aarch64": "arm64",
        }[platform.machine()]
    except KeyError:
        raise Exception(
            f"Your architecture '{platform.machine()}' seems to be unsupported"
            "by gotify-server. If this assumption is incorrect, "
            "please create an issue on github."
        )

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

        import requests

        r = requests.get(
            "https://github.com/gotify/server/releases/latest",
            allow_redirects=True,
        )
        tag_name = r.url.split("/")[-1]

        r = requests.get(
            f"https://github.com/gotify/server/releases/download/{tag_name}/{gotify_binary}.zip",
            allow_redirects=True,
        )
        r.raise_for_status()

        zipfile.ZipFile(BytesIO(r.content)).extractall(test_server_dir)
        if system == "linux":
            subprocess.run(["chmod", "+x", str(gotify_binary_path)])

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
        try:
            session.run("coverage", "run", "-m", "pytest")
        finally:
            p.kill()
            session.run("coverage", "report")
