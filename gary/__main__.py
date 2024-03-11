"""The entrypoint for the bot."""
#  Copyright (c) 2024  Cypheriel
from importlib import resources
from logging import getLogger
from os import getenv

from discord import Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv

from gary.logging import setup_logging

setup_logging()
load_dotenv()

logger = getLogger("gary")
bot = Bot(intents=Intents.all())

COGS: list[str] = [
    dir.name[:-3]
    for dir in (resources.files(__package__) / "cogs").iterdir()
    if not dir.name.startswith("_") and dir.name.endswith(".py")
]


@bot.event
async def on_ready() -> None:
    """
    Express the readiness of the bot to receive events and commands.

    Additionally signal to Pterodactyl that the bot has started and is running.
    """
    if cog_count := len(bot.cogs):
        s = "s" if cog_count != 1 else ""
        logger.info(f"[cyan]Loaded {cog_count} cog{s}[/]")

    if command_count := len(bot.commands):
        s = "s" if command_count != 1 else ""
        logger.info(f"[cyan]Loaded {command_count} command{s}[/]")

    if application_command_count := len(bot.application_commands) - command_count:
        s = "s" if application_command_count != 1 else ""
        logger.info(f"[cyan]Loaded {application_command_count} application command{s}[/]")

    logger.info("[bold green]Bot is ready![/]")

    if (status_channel_id := getenv("BOT_STATUS_CHANNEL_ID")) is not None:
        bot_status_channel = bot.get_channel(int(status_channel_id))
        await bot_status_channel.send("Howdy! I'm online and ready. Any reminder timers have been reset.")


if __name__ == "__main__":
    for cog in COGS:
        logger.info(f"[cyan]Loading the [bright_cyan]{cog.replace('_', ' ').title()}[/] cog...[/]")
        bot.load_extension(f"gary.cogs.{cog}")

    bot.run(getenv("TOKEN"))
