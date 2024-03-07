import asyncio
from datetime import timedelta, datetime, tzinfo

from discord import Message, Bot, slash_command, ApplicationContext, TextChannel
from discord.ext.commands import Cog

DISBOARD_ID = 302050872383242240


async def bump_reminder(channel: TextChannel) -> None:
    await channel.send(
        f"Howdy, <@&1210376856264773672>! It's time to bump the server!\n"
        "</bump:947088344167366698>"
    )


class BumpReminder(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.last_bump: datetime | None = None

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.id == DISBOARD_ID and len(message.embeds) == 1 and "Bump done!" in message.embeds[0].description:
            if self.last_bump is not None and (message.created_at - self.last_bump).total_seconds() < timedelta(hours=2).total_seconds():
                await message.channel.send("Whoa! Double bump!")
                return

            await message.channel.send("Thanks for the bump! I'll remind you to bump again in 2 hours.")
            self.last_bump = message.created_at

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
