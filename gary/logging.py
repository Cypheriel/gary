"""Module responsible for initialising logging for the bot."""
import logging

from rich.logging import RichHandler


def setup_logging() -> None:
    """Set up logging for the bot."""
    logging.getLogger("discord").setLevel(logging.WARNING)

    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[
            RichHandler(markup=True, rich_tracebacks=True),
        ],
        force=True,
    )
