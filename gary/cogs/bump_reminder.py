import asyncio

from discord.ext.commands import Cog
from discord import Message, Bot

DISBOARD_ID = 302050872383242240


class BumpReminder(Cog):
    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.author.id == DISBOARD_ID and any("Bump done!" in embed.description for embed in message.embeds):
            await asyncio.sleep(2 * 60 * 60)  # 2 hours
            await message.channel.send(f"Howdy, <@&1210376856264773672>! It's time to bump the server!")


def setup(bot: Bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(BumpReminder(bot))
