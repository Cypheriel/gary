#  Copyright (c) 2024  Cypheriel
import asyncio
from datetime import timedelta, datetime, timezone

import discord
from discord import Message, Bot, slash_command, ApplicationContext, TextChannel, Embed, EmbedField
from discord.ext.commands import Cog

DISBOARD_ID = 302050872383242240


async def bump_reminder(channel: TextChannel) -> None:
    await channel.send(f"Howdy, <@&1210376856264773672>! It's time to bump the server!\n</bump:947088344167366698>")


class BumpReminder(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.last_bump: datetime = datetime.fromtimestamp(0, timezone.utc)
        self.has_bumped = False

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if (
            message.author.id != DISBOARD_ID
            or len(message.embeds) != 1
            or "Bump done!" not in message.embeds[0].description
            or message.interaction is None
            or message.interaction.name != "bump"
        ):
            return

        time_since_last_bump = message.created_at - self.last_bump
        target_offset = (time_since_last_bump - timedelta(hours=2)) if self.has_bumped else timedelta()

        if self.has_bumped and target_offset.total_seconds() < 0:
            await message.reply("Whoa! Double bump! ✨")
            return

        self.last_bump = message.created_at
        self.has_bumped = True

        disboard_latency = discord.Object(message.interaction.id).created_at - message.created_at
        next_reminder = self.last_bump + timedelta(hours=2)

        await message.reply(
            embed=Embed(
                description=f"Thank you for bumping! I will remind you to bump again <t:{int(next_reminder.timestamp())}:R>.",
                fields=[
                    EmbedField(name="Offset", value=f"{target_offset}", inline=True),
                    EmbedField(name="API Latency", value=f"{self.bot.latency * 1000:.2f}ms", inline=True),
                    EmbedField(name="Disboard Latency", value=f"{disboard_latency}", inline=True),
                ],
                color=0x90EEBF
            )
        )

        time_to_sleep = int((next_reminder - datetime.now(timezone.utc)).total_seconds())

        await asyncio.sleep(time_to_sleep)
        await bump_reminder(message.channel)

    @slash_command()
    async def bump_remind(self, ctx: ApplicationContext, hours: int = 0, minutes: int = 0, seconds: int = 0):
        await ctx.respond(f"Reminder set for {hours}h {minutes}m {seconds}s!", ephemeral=True)

        time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        await asyncio.sleep(time.seconds)
        await bump_reminder(ctx.channel)


def setup(bot: Bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(BumpReminder(bot))
