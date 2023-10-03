from discord import ui, Message, Interaction, InteractionResponse, message_command, Cog, Embed, ButtonStyle, \
    ApplicationContext, Thread, Member, User, TextChannel, VoiceChannel
from discord.ui import Button, Select


class MoveConversationMenu(ui.View):
    def __init__(self, original_message: Message):
        super().__init__()

        self.channel_selection: TextChannel | Thread | VoiceChannel | None = None
        self.user_selection: list[Member | User] | None = None

        self.original_message = original_message

    @ui.channel_select()
    async def channel_select(self, select: Select, interaction: Interaction):
        assert isinstance(interaction.response, InteractionResponse)

        if len(select.values) != 1:
            return

        channel = select.values[0]
        assert isinstance(channel, TextChannel | Thread | VoiceChannel)

        self.channel_selection = channel

        await interaction.response.defer()

    @ui.user_select(placeholder="Select users to notify of the move", min_values=0, max_values=5)
    async def user_select(self, select: Select, interaction: Interaction):
        values: list[User | Member] = [val for val in select.values if isinstance(val, User | Member)]

        if len(values) != len(select.values):
            return

        self.user_selection = values

        await interaction.response.defer()

    @ui.button(label="Move conversation", style=ButtonStyle.green)
    async def move_conversation(self, _button: Button, interaction: Interaction):
        if not self.channel_selection:
            return

        original_channel = self.original_message.channel
        if not isinstance(original_channel, TextChannel | Thread | VoiceChannel):
            return

        from_embed = Embed(
            title=f"From {original_channel.mention}",
            description=f"{self.original_message.author.mention}: {self.original_message.content[:1_500]}",
            url=self.original_message.jump_url,
        )

        if self.original_message.attachments:
            from_embed.set_footer(text="Attachments were provided in the original reported_message.")

        user_mentions = None
        if self.user_selection:
            user_mentions = ", ".join(
                user.mention for user in self.user_selection if self.original_message.author != user
            )

        moved_message = await self.channel_selection.send(
            content=user_mentions,
            embed=from_embed
        )

        await self.original_message.reply(embed=Embed(
            title=f"✅ Moved conversation to {self.channel_selection.mention}",
            url=moved_message.jump_url,
        ))

        assert isinstance(interaction.response, InteractionResponse)

        await interaction.response.edit_message(content="Moved conversation!", view=None)


class MoveConversations(Cog):
    @message_command()
    async def move_conversation(self, ctx: ApplicationContext, message: Message):
        await ctx.respond(view=MoveConversationMenu(message), ephemeral=True)
