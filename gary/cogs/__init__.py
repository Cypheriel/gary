"""This package contains all the cogs used by the Gary bot."""
from typing import Type

from discord.ext.commands import Bot, Cog
from rich.console import Console

from .move_conversation import MoveConversations
from .ping import Ping
from .report import Report

console = Console()

cogs: list[Type[Cog]] = [
    Ping,
    MoveConversations,
    Report,
]


def load_cogs(bot: Bot):
    """Load all the cogs in the cogs list."""
    for cog in cogs:
        console.print(f"[cyan]Loading the [bright_cyan]{cog.__name__}[/] cog...[/]")
        bot.add_cog(cog(bot))
