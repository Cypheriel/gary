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

        self.positions: list[Message | None] = [None, None]

    @message_command(name="Set position — 1")
    async def set_mass_delete_position_1(self, ctx: ApplicationContext, message: Message):
        """Set the first position of a mass action."""
        self.positions[0] = message

        await ctx.respond("Set position 1", ephemeral=True)

    @message_command(name="Set position — 2")
    async def set_mass_delete_position_2(self, ctx: ApplicationContext, message: Message):
        """Set the second position of a mass action."""
        self.positions[1] = message

        await ctx.respond("Set position 2", ephemeral=True)

    @pma_group.command()
    @default_permissions(manage_messages=True)
    async def delete(self, ctx: ApplicationContext):
        """Delete all messages between the two positions."""
        if None in self.positions:
            await ctx.respond("Please set both positions first", ephemeral=True)
            return

        assert isinstance(self.positions[0], Message)
        assert isinstance(self.positions[1], Message)

        position_1: Message = self.positions[0]
        position_2: Message = self.positions[1]

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
