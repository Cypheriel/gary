"""The entrypoint for the bot."""
from logging import getLogger
from os import getenv
from pathlib import Path

from discord import Intents
from discord.ext.commands import Bot
from dotenv import load_dotenv
from mypy import api as mypy_api

from gary.cogs import load_cogs
from gary.logging import setup_logging

setup_logging()
load_dotenv()

logger = getLogger("gary")
bot = Bot(intents=Intents.all())


@bot.event
async def on_ready():
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
    await bot.sync_commands()


if __name__ == "__main__":
    logger.info("Running type-checker...")
    result = mypy_api.run([str(Path(__file__).parent)])

    if stdout := result[0]:
        logger.info(f"[yellow]Type-checking report[/]:\n{stdout.strip()}")

    if stderr := result[1]:
        logger.error(stderr)

    if (exit_code := result[2]) != 0:
        logger.debug(f"[bold red]Exited with exit code [bright_red]{exit_code}[/][/]")
        exit(exit_code)

    load_cogs(bot)

    bot.run(getenv("TOKEN"))
