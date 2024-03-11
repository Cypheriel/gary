"""Module responsible for initialising logging for the bot."""
#  Copyright (c) 2024  Cypheriel
import logging
from os import environ

from rich.console import Console
from rich.logging import RichHandler


def setup_logging() -> None:
    """Set up logging for the bot."""
    logging.getLogger("discord").setLevel(logging.WARNING)

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(
                console=Console(
                    width=123 if environ.get("USER") == "container" else None,
                ),
                markup=True,
                rich_tracebacks=True,
            ),
        ],
        force=True,
    )
