"""The entrypoint for the bot."""
from os import getenv
from pathlib import Path

from discord.ext import commands
from dotenv import load_dotenv
from mypy import api as mypy_api
from rich.console import Console

from gary.cogs import load_cogs

load_dotenv()

console = Console()
bot = commands.Bot()


@bot.event
async def on_ready():
    """
    Express the readiness of the bot to receive events and commands.

    Additionally signal to Pterodactyl that the bot has started and is running.
    """
    console.print("[bold green]Bot is ready![/]")
    await bot.sync_commands()


if __name__ == "__main__":
    console.print("[bold]Running mypy...[/bold]", end="\n\n")
    result = mypy_api.run([str(Path(__file__).parent)])

    if stdout := result[0]:
        console.print(f"[yellow]Type-checking report[/]:\n\t{stdout}")

    if stderr := result[1]:
        console.print(f"[bold red]Error report[/]:\n{stderr}")

    if (exit_code := result[2]) != 0:
        console.print(f"[bold red]Exited with exit code [bright_red]{exit_code}[/][/]")
        exit(exit_code)

    load_cogs(bot)
    console.print()
    console.print(f"[cyan]Loaded {len(bot.cogs)} cogs[/]")
    console.print(f"[cyan]Loaded {len(bot.commands)} commands[/]")
    console.print(
        f"[cyan]Loaded {len(bot.all_commands)} application commands[/]",
        end="\n\n",
    )
    bot.run(getenv("TOKEN"))
