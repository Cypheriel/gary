"""Module containing the MoveConversations cog and related functionality."""
from discord import (
    ApplicationContext,
    Bot,
    ButtonStyle,
    ChannelType,
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
from discord.ui import Select


class MoveConversationButton(ui.Button):
    """A button for moving a conversation."""

    def __init__(self, menu: "MoveConversationMenu", *args, **kwargs):
        """Create a new MoveConversationButton instance tied to the MoveConversationMenu."""
        super().__init__(
            label="Move conversation",
            style=ButtonStyle.primary,
            *args,
            **kwargs,
        )

        self.menu = menu

    async def callback(self, interaction: Interaction):
        """Move the conversation to the selected channel upon press."""
        if not self.menu.channel_selection:
            return

        original_channel = self.menu.original_message.channel
        assert isinstance(original_channel, TextChannel | Thread | VoiceChannel)

        description = (
            f"{self.menu.original_message.author.mention}: {self.menu.original_message.content[:1_500]}"
            if self.menu.original_message.content
            else None
        )

        from_embed = Embed(
            title=f"From {original_channel.mention}",
            description=description,
            url=self.menu.original_message.jump_url,
        )

        if attachments := self.menu.original_message.attachments:
            s = "s" if len(attachments) != 1 else ""
            were = "were" if s else "was"
            from_embed.set_footer(
                text=f"Attachment{s} {were} provided in the original message.",
            )

        if self.menu.original_message.embeds:
            s = "s" if len(self.menu.original_message.embeds) != 1 else ""
            were = "were" if s else "was"
            from_embed.set_footer(
                text=f"Embed{s} {were} provided in the original message.",
            )

        user_mentions = None
        if self.menu.user_selection:
            user_mentions = ", ".join(
                user.mention for user in self.menu.user_selection if self.menu.original_message.author != user
            )

        moved_message = await self.menu.channel_selection.send(
            content=user_mentions,
            embed=from_embed,
        )

        await self.menu.original_message.reply(
            embed=Embed(
                title=f"➡️ Moved conversation to {self.menu.channel_selection.mention}",
                url=moved_message.jump_url,
            ),
        )

        assert isinstance(interaction.response, InteractionResponse)

        await interaction.response.edit_message(
            content="Moved conversation!",
            view=None,
        )


class MoveConversationMenu(ui.View):
    """A view containing the UI elements and logic for moving a conversation."""

    @property
    def valid(self):
        """Return whether the current selection is valid."""
        return self._valid

    @valid.setter
    def valid(self, value):
        """Reset the button's disabled state based on the validity of the current selection."""
        self._valid = value

        self.remove_item(self.button)
        self.button.disabled = not value
        self.add_item(self.button)

    def __init__(self, original_message: Message):
        """Create a new MoveConversationMenu instance tied to a specific message."""
        super().__init__()

        self._valid = False
        self.channel_selection: TextChannel | Thread | VoiceChannel | None = None
        self.user_selection: list[Member | User] | None = None

        self.original_message = original_message
        self.button = MoveConversationButton(self, disabled=True)
        self.add_item(self.button)

    @ui.channel_select(channel_types=[ChannelType.text, ChannelType.voice, ChannelType.public_thread])
    async def channel_select(self, select: Select, interaction: Interaction):
        """Present a channel selection menu for the channel to move a conversation to the user."""
        assert isinstance(interaction.response, InteractionResponse)

        if not select.channel_types or len(select.values) != 1:
            return

        channel = select.values[0]

        assert isinstance(self.original_message.author, Member)
        assert isinstance(interaction.user, Member)

        valid_channel_type = isinstance(channel, TextChannel | Thread | VoiceChannel)

        if not valid_channel_type:
            self.valid = False
            await interaction.response.edit_message(content="❌ This is not a valid chat channel!", view=self)
            return

        assert isinstance(channel, TextChannel | Thread | VoiceChannel)

        if channel == self.original_message.channel:
            self.valid = False
            await interaction.response.edit_message(
                content="❌ You can't move a conversation to the same channel!",
                view=self,
            )
            return

        if (
            not channel.permissions_for(self.original_message.author).send_messages
            or not channel.permissions_for(interaction.user).send_messages
        ):
            self.valid = False
            await interaction.response.edit_message(
                content="❌ You don't have permission to move this message to that channel!",
                view=self,
            )
            return

        self.valid = True
        await interaction.response.edit_message(content=None, view=self)

        self.channel_selection = channel

        # await interaction.response.defer()

    @ui.user_select(
        placeholder="Select users to notify of the move",
        min_values=0,
        max_values=5,
    )
    async def user_select(self, select: Select, interaction: Interaction):
        """Present a user selection menu for the users to notify of the move."""
        values: list[Member | User] = [val for val in select.values if isinstance(val, Member | User)]

        assert len(values) == len(select.values)

        self.user_selection = values

        await interaction.response.defer()


class MoveConversations(Cog):
    """A cog containing context menu command for moving conversations."""

    @message_command(name="Move conversation")
    async def move_conversation(self, ctx: ApplicationContext, message: Message):
        """Present the move conversation menu to the user."""
        if message.author == ctx.bot.user:
            await ctx.respond(content="I can't move my own messages!", ephemeral=True)
            return

        await ctx.respond(view=MoveConversationMenu(message), ephemeral=True)


def setup(bot: Bot):
    """Add the MoveConversations cog to the bot."""
    bot.add_cog(MoveConversations(bot))
