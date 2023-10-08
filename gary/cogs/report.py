"""Module containing the Report cog and related functionality."""
from discord import (
    ApplicationContext,
    Bot,
    ButtonStyle,
    CategoryChannel,
    Embed,
    EmbedField,
    ForumChannel,
    Interaction,
    InteractionResponse,
    Member,
    Message,
    SelectOption,
    StageChannel,
    User,
    message_command,
    ui,
    user_command,
)
from discord.ext.commands import Cog

RULES: list[str] = [
    "Follow Discord's Terms of Service and Community Guidelines.",
    "No matter what, treat members with the utmost respect.",
    "Keep discussion in English as best you can.",
    "Do not post unapproved advertisements.",
    "Do not exploit implemented systems, bots, or interfaces.",
    "Keeps discussions relevant to channel topics to the best of your ability.",
    "Follow the directives of moderators.",
    "No sexually implicit messages or content.",
    "Do not post content or messages that are politically, religiously, or otherwise controversial in nature.",
]

RULES_OPTIONS = [SelectOption(label=f"Rule #{i} — {rule}"[:100], value=str(i)) for i, rule in enumerate(RULES, start=1)]


class ReportView(ui.View):
    """A view containing the UI elements and logic for reporting a user or message."""

    def __init__(
        self,
        reported_message: Message | None = None,
        user: User | Member | None = None,
    ):
        """Create a new ReportView instance tied to a specific message or user."""
        super().__init__()

        self.rule_violations: list[int] | None = None
        self.reported_message = reported_message

        reported_user = reported_message.author if reported_message else user
        assert reported_user is not None

        self.user = reported_user

    @ui.string_select(
        placeholder="Select rule violation(s)",
        min_values=1,
        max_values=len(RULES),
        options=RULES_OPTIONS,
    )
    async def rule_violations_select(self, select: ui.Select, interaction: Interaction):
        """Present a rule violation selection menu for the user."""
        assert isinstance(interaction.response, InteractionResponse)
        self.rule_violations = [int(val) for val in select.values if isinstance(val, str) and val.isdigit()]
        await interaction.response.defer()

    @ui.button(label="Report", style=ButtonStyle.red)
    async def report(self, _button: ui.Button, interaction: Interaction):
        """Report the user or message upon press."""
        assert interaction.user is not None
        assert isinstance(interaction.response, InteractionResponse)

        if not self.rule_violations:
            return

        guild = interaction.guild
        if not guild:
            return

        report_channel = guild.get_channel_or_thread(1158655735413084231)
        if not report_channel or isinstance(
            report_channel,
            StageChannel | ForumChannel | CategoryChannel,
        ):
            return

        await report_channel.send(
            embeds=[
                Embed(
                    title="Report",
                    fields=[
                        EmbedField(
                            name="User",
                            value=self.user.mention,
                            inline=True,
                        ),
                        EmbedField(
                            name="Reporter",
                            value=interaction.user.mention,
                            inline=True,
                        ),
                        EmbedField(
                            name="Message",
                            value=f'"{self.reported_message.content}" ([link]({self.reported_message.jump_url}))'
                            if self.reported_message
                            else "N/A",
                        ),
                    ],
                ),
                Embed(
                    title="Alleged Rule Violations",
                    fields=[
                        EmbedField(name=f"Rule #{i}", value=RULES[i - 1], inline=False)
                        for i in sorted(self.rule_violations)
                    ],
                ),
            ],
        )

        await interaction.response.edit_message(
            content="You report has been sent. Thank you for helping keep the server safe!",
            view=None,
        )


class Report(Cog):
    """A cog containing commands for reporting users and messages."""

    @message_command(name="Report message")
    async def report_message(self, ctx: ApplicationContext, message: Message):
        """Present a report view for the given message."""
        await ctx.send_response(
            view=ReportView(reported_message=message),
            ephemeral=True,
        )

    @user_command(name="Report user")
    async def report_user(self, ctx: ApplicationContext, user: User):
        """Present a report view for the given user."""
        await ctx.send_response(
            view=ReportView(user=user),
            ephemeral=True,
        )


def setup(bot: Bot):
    """Set up the Report cog."""
    bot.add_cog(Report(bot))
