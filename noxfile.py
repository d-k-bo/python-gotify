import nox

nox.options.sessions = ["format", "lint", "mypy", "test"]


@nox.session
def format(session: nox.Session):
    session.install("black", "isort")
    session.run("isort", ".")
    session.run("black", ".")


@nox.session
def check_format(session: nox.Session):
    session.install("black", "isort")
    session.run("isort", ".", "--check")
    session.run("black", ".", "--check")


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
    session.install(".[stream]", "mypy", "pytest")
    session.run("mypy")


@nox.session(python=["3.9", "3.10"])
def test(session: nox.Session):
    session.install(
        ".[stream]",
        "coverage",
        "pytest",
        "pytest-asyncio",
        "trycast",
    )
    try:
        session.run("coverage", "run", "-m", "pytest")
    finally:
        session.run("coverage", "report")
