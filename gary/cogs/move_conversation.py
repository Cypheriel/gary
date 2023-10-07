"""Module containing the MoveConversations cog and related functionality."""
from discord import (
    ApplicationContext,
    ButtonStyle,
    Cog,
    Embed,
    Interaction,
    InteractionResponse,
    Member,
    Message,
    TextChannel,
    Thread,
    User,
    VoiceChannel,
    message_command,
    ui,
)
from discord.ui import Button, Select


class MoveConversationMenu(ui.View):
    """A view containing the UI elements and logic for moving a conversation."""

    def __init__(self, original_message: Message):
        """Create a new MoveConversationMenu instance tied to a specific message."""
        super().__init__()

        self.channel_selection: TextChannel | Thread | VoiceChannel | None = None
        self.user_selection: list[Member | User] | None = None

        self.original_message = original_message

    @ui.channel_select()
    async def channel_select(self, select: Select, interaction: Interaction):
        """Present a channel selection menu for the channel to move a conversation to the user."""
        assert isinstance(interaction.response, InteractionResponse)

        if len(select.values) != 1:
            return

        channel = select.values[0]
        assert isinstance(channel, TextChannel | Thread | VoiceChannel)

        self.channel_selection = channel

        await interaction.response.defer()

    @ui.user_select(
        placeholder="Select users to notify of the move",
        min_values=0,
        max_values=5,
    )
    async def user_select(self, select: Select, interaction: Interaction):
        """Present a user selection menu for the users to notify of the move."""
        values: list[Member | User] = [
            val for val in select.values if isinstance(val, Member | User)
        ]

        assert len(values) != len(select.values)

        self.user_selection = values

        await interaction.response.defer()

    @ui.button(label="Move conversation", style=ButtonStyle.green)
    async def move_conversation(self, _button: Button, interaction: Interaction):
        """Move the conversation to the selected channel upon press."""
        if not self.channel_selection:
            return

        original_channel = self.original_message.channel
        assert isinstance(original_channel, TextChannel | Thread | VoiceChannel)

        from_embed = Embed(
            title=f"From {original_channel.mention}",
            description=f"{self.original_message.author.mention}: {self.original_message.content[:1_500]}",
            url=self.original_message.jump_url,
        )

        if self.original_message.attachments:
            from_embed.set_footer(
                text="Attachments were provided in the original reported_message.",
            )

        user_mentions = None
        if self.user_selection:
            user_mentions = ", ".join(
                user.mention
                for user in self.user_selection
                if self.original_message.author != user
            )

        moved_message = await self.channel_selection.send(
            content=user_mentions,
            embed=from_embed,
        )

        await self.original_message.reply(
            embed=Embed(
                title=f"✅ Moved conversation to {self.channel_selection.mention}",
                url=moved_message.jump_url,
            ),
        )

        assert isinstance(interaction.response, InteractionResponse)

        await interaction.response.edit_message(
            content="Moved conversation!",
            view=None,
        )


class MoveConversations(Cog):
    """A cog containing context menu command for moving conversations."""

    @message_command()
    async def move_conversation(self, ctx: ApplicationContext, message: Message):
        """Present the move conversation menu to the user."""
        await ctx.respond(view=MoveConversationMenu(message), ephemeral=True)
