from discord import slash_command, ApplicationContext
from discord.ext.commands import Cog


class Ping(Cog):
    @slash_command()
    async def ping(self, ctx: ApplicationContext):
        latency = round(ctx.bot.latency * 1000, 2)
        await ctx.trigger_typing()

        await ctx.respond(f"Pong! Latency: {latency:.2f}ms")
