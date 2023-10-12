"""Module containing the Ping cog."""
from discord import ApplicationContext, Bot, slash_command
from discord.ext.commands import Cog


class Ping(Cog):
    """Cog containing the ping command."""

    @slash_command()
    async def ping(self: "Ping", ctx: ApplicationContext) -> None:
        """Report the bot's latency."""
        latency = round(ctx.bot.latency * 1000, 2)
        await ctx.trigger_typing()

        await ctx.respond(f"Pong! Latency: {latency:.2f}ms")


def setup(bot: Bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(Ping(bot))
