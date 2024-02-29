import asyncio
from datetime import timedelta

from discord import Message, Bot, slash_command, ApplicationContext, TextChannel
from discord.ext.commands import Cog

DISBOARD_ID = 302050872383242240


async def bump_reminder(channel: TextChannel) -> None:
    await channel.send(
        f"Howdy, <@&1210376856264773672>! It's time to bump the server!\n"
        "</bump:947088344167366698>"
    )


class BumpReminder(Cog):
    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.id == DISBOARD_ID and any("Bump done!" in embed.description for embed in message.embeds):
            await asyncio.sleep(2 * 60 * 60)  # 2 hours
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
