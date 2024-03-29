"""Module containing the PrecisionMassActions cog and related functionality."""
#  Copyright (c) 2024  Cypheriel
from discord import (
    ApplicationContext,
    Bot,
    Cog,
    Message,
    SlashCommandGroup,
    TextChannel,
    Thread,
    VoiceChannel,
    default_permissions,
    message_command,
)


class PrecisionMassActions(Cog):
    """Cog containing commands for performing precision mass actions."""

    pma_group = SlashCommandGroup(name="pma", description="Precision mass actions")

    def __init__(self: "PrecisionMassActions", bot: Bot) -> None:
        """Initialize the cog."""
        super().__init__()

        self.bot = bot

        self.positions: dict[int, list[Message | None]] = {}

    @message_command(name="Set position — 1")
    async def set_mass_delete_position_1(
        self: "PrecisionMassActions",
        ctx: ApplicationContext,
        message: Message,
    ) -> None:
        """Set the first position of a mass action."""
        if self.positions.get(ctx.user.id) is None:
            self.positions[ctx.user.id] = [message, None]

        else:
            self.positions[ctx.user.id][0] = message

        await ctx.respond("Set position 1", ephemeral=True)

    @message_command(name="Set position — 2")
    async def set_mass_delete_position_2(
        self: "PrecisionMassActions",
        ctx: ApplicationContext,
        message: Message,
    ) -> None:
        """Set the second position of a mass action."""
        if self.positions.get(ctx.user.id) is None:
            self.positions[ctx.user.id] = [None, message]
        else:
            self.positions[ctx.user.id][1] = message

        await ctx.respond("Set position 2", ephemeral=True)

    @pma_group.command()
    @default_permissions(manage_messages=True)
    async def delete(self: "PrecisionMassActions", ctx: ApplicationContext) -> None:
        """Delete all messages between the two positions."""
        positions = self.positions.get(ctx.user.id, [None, None])

        if positions is None or None in positions:
            await ctx.respond("Please set both positions first", ephemeral=True)
            return

        assert isinstance(positions[0], Message)
        assert isinstance(positions[1], Message)

        if positions[0].channel != positions[1].channel:
            await ctx.respond("Please select two messages from the same channel!", ephemeral=True)
            return

        assert isinstance(positions[0].channel, TextChannel | VoiceChannel | Thread)
        channel: TextChannel | VoiceChannel | Thread = positions[0].channel

        if positions[0].created_at > positions[1].created_at:
            positions[0], positions[1] = positions[1], positions[0]

        message_history = await channel.history(
            after=positions[0],
            before=positions[1],
        ).flatten()

        messages: list[Message] = [
            positions[0],
            *[message for message in message_history if message is not None],
            positions[1],
        ]

        if len(messages) in (0, 1):
            await ctx.respond("Please select more than one message!", ephemeral=True)
            return

        await channel.delete_messages(messages)

        await ctx.respond(f"✅ Deleted {len(messages)} messages.", ephemeral=True)


def setup(bot: Bot) -> None:
    """Set up the cog."""
    bot.add_cog(PrecisionMassActions(bot))
