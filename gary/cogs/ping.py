"""Module containing the Ping cog."""
import asyncio

from discord import ApplicationContext, Bot, slash_command
from discord.ext.commands import Cog


class Ping(Cog):
    """Cog containing the ping command."""

    @slash_command()
    async def ping(self: "Ping", ctx: ApplicationContext) -> None:
        """Report the bot's average latency."""
        await ctx.trigger_typing()

        total_latency = 0
        for _ in range(5):
            total_latency += ctx.bot.latency
            await asyncio.sleep(0.5)

        await ctx.respond(f"Pong! Average latency: {total_latency / 5:.2f}ms")


def setup(bot: Bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(Ping(bot))
