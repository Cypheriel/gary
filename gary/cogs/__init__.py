"""This package contains all the cogs used by the Gary bot."""
from logging import getLogger
from typing import Type

from discord.ext.commands import Bot, Cog

from .move_conversation import MoveConversations
from .ping import Ping
from .report import Report

logger = getLogger(__name__)

cogs: list[Type[Cog]] = [
    Ping,
    MoveConversations,
    Report,
]


def load_cogs(bot: Bot):
    """Load all the cogs in the cogs list."""
    for cog in cogs:
        logger.info(f"[cyan]Loading the [bright_cyan]{cog.__name__}[/] cog...[/]")
        bot.add_cog(cog(bot))
