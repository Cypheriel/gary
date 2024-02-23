"""Module containing the Ping cog."""
import asyncio
import math
from datetime import datetime, timezone
from typing import Final

import discord
from discord import ApplicationContext, Bot, slash_command, Embed, EmbedField
from discord.ext.commands import Cog

PASSES: Final = 5
PASS_DELAY: Final = 45


class Ping(Cog):
    """Cog containing the ping command."""

    @slash_command()
    async def ping(self: "Ping", ctx: ApplicationContext) -> None:
        """Report the bot's average latency."""
        trigger_time = datetime.now(tz=timezone.utc)
        received_time = discord.Object(id=ctx.interaction.id).created_at
        delta_ms = (trigger_time - received_time).total_seconds() * 1_000

        await ctx.trigger_typing()
        await ctx.defer()

        results = []
        for i in range(1, PASSES + 1):
            results.append(ctx.bot.latency * 1_000)

            complete = False
            description = f"Latency test in progress..."
            if len(results) == PASSES:
                complete = True
                description = "Latency test complete!"

            embed = Embed(
                title="Pong...?" if not complete else "Pong! 🏓",
                description=description,
                fields=[
                    EmbedField(
                        name=f"Passes{f' ({i}/{PASSES})' if i != PASSES else ''}",
                        value=", ".join(f"{latency:.2f}ms" for latency in results)
                    ),
                    EmbedField(
                        name="Configured Delay",
                        value=f"{PASS_DELAY:.2f}s",
                    ),
                    EmbedField(
                        name="Average",
                        value=f"{sum(results) / len(results):.2f}ms",
                        inline=True
                    ),
                    EmbedField(
                        name="Minimum",
                        value=f"{min(results):.2f}ms",
                        inline=True
                    ),
                    EmbedField(
                        name="Maximum",
                        value=f"{max(results):.2f}ms",
                        inline=True
                    ),
                    EmbedField(
                        name="Reception Delta",
                        value=f"{delta_ms:.2f}ms{' ⚠' if delta_ms < 0 else ''}"
                    )
                ],
                color=discord.Color.blurple() if complete else discord.Color.gold(),
            )

            if not ctx.response.is_done:
                await ctx.respond(embed=embed)
            else:
                await ctx.edit(embed=embed)

            if complete:
                break

            with ctx.typing():
                await asyncio.sleep(PASS_DELAY)


def setup(bot: Bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(Ping(bot))
