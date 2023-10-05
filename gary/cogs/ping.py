"""Module containing the Ping cog."""
from discord import ApplicationContext, slash_command
from discord.ext.commands import Cog


class Ping(Cog):
    """Cog containing the ping command."""

    @slash_command()
    async def ping(self, ctx: ApplicationContext):
        """Report the bot's latency."""
        latency = round(ctx.bot.latency * 1000, 2)
        await ctx.trigger_typing()

        await ctx.respond(f"Pong! Latency: {latency:.2f}ms")
