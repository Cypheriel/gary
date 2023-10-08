"""Module containing the PrecisionMassActions cog and related functionality."""
from discord import (
    ApplicationContext,
    Bot,
    Cog,
    Message,
    SlashCommandGroup,
    default_permissions,
    message_command,
)


class PrecisionMassActions(Cog):
    """Cog containing commands for performing precision mass actions."""

    pma_group = SlashCommandGroup(name="pma", description="Precision mass actions")

    def __init__(self, bot: Bot):
        """Initialize the cog."""
        super().__init__()

        self.bot = bot

        self.positions: dict[int, list[Message | None]] = {}

    @message_command(name="Set position — 1")
    async def set_mass_delete_position_1(self, ctx: ApplicationContext, message: Message):
        """Set the first position of a mass action."""
        if self.positions.get(ctx.user.id) is None:
            self.positions[ctx.user.id] = [message, None]

        else:
            self.positions[ctx.user.id][0] = message

        await ctx.respond("Set position 1", ephemeral=True)

    @message_command(name="Set position — 2")
    async def set_mass_delete_position_2(self, ctx: ApplicationContext, message: Message):
        """Set the second position of a mass action."""
        if self.positions.get(ctx.user.id) is None:
            self.positions[ctx.user.id] = [None, message]
        else:
            self.positions[ctx.user.id][1] = message

        await ctx.respond("Set position 2", ephemeral=True)

    @pma_group.command()
    @default_permissions(manage_messages=True)
    async def delete(self, ctx: ApplicationContext):
        """Delete all messages between the two positions."""
        positions = self.positions.get(ctx.user.id, [None, None])

        if positions is None or None in positions:
            await ctx.respond("Please set both positions first", ephemeral=True)
            return

        if positions[0].channel != positions[1].channel:
            await ctx.respond("Please select two messages from the same channel!", ephemeral=True)
            return

        assert isinstance(positions[0], Message)
        assert isinstance(positions[1], Message)

        position_1: Message = positions[0]
        position_2: Message = positions[1]

        if position_1.created_at > position_2.created_at:
            position_1, position_2 = position_2, position_1

        messages = await ctx.channel.history(
            after=position_1,
            before=position_2,
        ).flatten() + [position_1, position_2]

        if len(messages) < 2:
            await ctx.respond("Please select more than one message!", ephemeral=True)
            return

        await ctx.channel.delete_messages(messages)

        await ctx.respond(f"✅ Deleted {len(messages)} messages.", ephemeral=True)


def setup(bot: Bot):
    """Set up the cog."""
    bot.add_cog(PrecisionMassActions(bot))
