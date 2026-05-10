import discord
from discord.ext import commands

COMMANDS_DATA = {
    "🍖 Hunger & Feeding": {
        "york feed": "Show York's hunger bar with an interactive Feed button.",
        "york status": "Check York's current hunger level and mood.",
        "york setchannel [#channel]": "Set where York posts automatic hunger alerts. (Manage Channels required)",
    },
    "💜 Trust System": {
        "york trust [@user]": "Check a user's trust level with York.",
        "york perks": "View all trust levels and their berry multiplier bonuses.",
    },
    "❓ Help": {
        "york help": "Show this help menu.",
    },
}


class CategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label=category, description=f"{len(cmds)} command(s)")
            for category, cmds in COMMANDS_DATA.items()
        ]
        super().__init__(placeholder="Select a command category...", options=options)

    async def callback(self, interaction: discord.Interaction):
        category = self.values[0]
        cmds = COMMANDS_DATA[category]
        embed = discord.Embed(
            title=f"🍖 York — {category}",
            color=discord.Color.purple(),
        )
        for name, desc in cmds.items():
            embed.add_field(name=f"`{name}`", value=desc, inline=False)
        embed.set_footer(text="Satellite 06 — York (Greed) | Hunger & Trust | Prefix: york")
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(CategorySelect())


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help", aliases=["?"])
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="🍖 YORK — Satellite 06 (Greed)",
            description=(
                "Hi, I'm York.\n"
                "I handle the most essential functions: eating, sleeping, and being fed by you.\n"
                "Feed me to build trust and unlock better berry rewards across the system.\n\n"
                "**Prefix:** `york`"
            ),
            color=discord.Color.purple(),
        )
        embed.set_footer(text="Select a category below to view commands.")
        await ctx.send(embed=embed, view=HelpView())


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
