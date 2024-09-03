from __future__ import annotations

from invoke import task
from invoke.context import Context
from invoke.terminals import WINDOWS


USE_PTY = not WINDOWS


@task
def test(context: Context) -> None:
    _ = context.run("pytest --cov --cov-fail-under=10 ./tests", echo=True, pty=True)


@task
def validate(context: Context) -> None:
    """validate"""
    _ = context.run("pyflakes ./src", echo=True)
    _ = context.run("pyflakes ./tests", echo=True)
    _ = context.run("black --check --diff  --verbose .", echo=True)

    _ = context.run("pylint ./src", warn=True, echo=True)
    _ = context.run("pylint ./tests", warn=True, echo=True)

    _ = context.run("mypy --install-types --non-interactive ./src", echo=True)
    _ = context.run("mypy --install-types --non-interactive ./tests", echo=True)


@task
def fmt(context: Context) -> None:
    _ = context.run("black .")
