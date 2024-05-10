#  Copyright (c) 2024  Cypheriel
import asyncio
import logging
import re
from datetime import datetime, timezone

from discord import Message, Bot, NotFound, DeletedReferencedMessage
from discord.ext.commands import Cog

timestamp_regex = re.compile(r"<t:(\d+):d>")
logger = logging.getLogger(__name__)


class FreeGames(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.ping_messages: list[Message] = []

    @Cog.listener()
    async def on_message(self, message: Message) -> None:
        if message.channel.id != 1236159339388211260 or message.author.id == self.bot.user.id:
            return

        logger.debug(f"Message received in #free-games: {message.content}")

        await asyncio.sleep(0.250)

        task = await self.create_expiring_message(message)
        if task is not None:
            ping_message = await message.reply("<@&1236159897486364704>")
            self.ping_messages.append(ping_message)
            await self.create_expiring_message(ping_message)
            await self.prune_ping_messages()

    @Cog.listener()
    async def on_ready(self):
        free_games_channel = self.bot.get_channel(1236159339388211260)

        tasks = set()

        async for message in free_games_channel.history():
            if message.author.id == self.bot.user.id and message.content == "<@&1236159897486364704>":
                if isinstance(message.reference.resolved, DeletedReferencedMessage):
                    await message.delete(reason="Referenced message was deleted.")
                    continue

                self.ping_messages.append(message)

            if task := await self.create_expiring_message(message):
                tasks.add(task)

        self.ping_messages.sort(key=lambda m: m.created_at.timestamp(), reverse=True)
        for message in self.ping_messages[1:]:
            await message.delete(reason="Too many ping messages.")

        await asyncio.gather(*tasks)

    async def create_expiring_message(self, message: Message):
        if message.author.id == self.bot.user.id or message.content:
            return

        latest_expiration_time = None

        for embed in message.embeds:
            logger.debug(f"Checking embed: {embed.description}")
            match = timestamp_regex.search(embed.description)
            if not match:
                break

            time_until_expiration = int(match.group(1)) - int(datetime.now(timezone.utc).timestamp())

            if latest_expiration_time is None or time_until_expiration > latest_expiration_time:
                latest_expiration_time = time_until_expiration

        if latest_expiration_time is None or latest_expiration_time < 0:
            await message.delete(reason="Free game message does not contain a valid expiration time.")
            return

        logger.debug(f"Message will expire in {latest_expiration_time} seconds.")

        return asyncio.create_task(self.sleep_and_delete_message(message, latest_expiration_time))

    async def prune_ping_messages(self):
        self.ping_messages.sort(key=lambda m: m.created_at.timestamp(), reverse=True)

        for i, message in enumerate(self.ping_messages):
            if isinstance(message.reference.resolved, DeletedReferencedMessage):
                await message.delete(reason="Referenced message was deleted.")
                continue

            if i == 0:
                continue

            await message.delete(reason="Too many ping messages.")

        self.ping_messages = [self.ping_messages[0]]

    async def sleep_and_delete_message(self, message: Message, time_to_sleep: int):
        await asyncio.sleep(time_to_sleep)
        try:
            await message.delete(reason="Free game expired.")
            for ping_message in list(self.ping_messages):
                if ping_message.reference.message_id == message.id:
                    await ping_message.delete(reason="Free game expired.")
                    self.ping_messages.remove(ping_message)

        except NotFound:
            ...


def setup(bot: Bot) -> None:
    """Add the cog to the bot."""
    bot.add_cog(FreeGames(bot))
