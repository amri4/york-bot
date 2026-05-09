import discord
from discord.ext import commands

COMMANDS_DATA = {
    "🍖 Basic Needs": {
        "york eat <food>": "York eats something. Very important. Logged in the database.",
        "york sleep": "York takes a nap. Duration is random.",
        "york claim <item>": "York claims an item for herself. It's hers now.",
        "york inventory": "Show everything York has claimed in this server.",
        "york take @user <amount>": "York takes coins from another user. For herself, obviously.",
        "york wallet": "Show York's total coins taken in this server.",
        "york siblings": "List all six Vegapunk satellites.",
    },
    "❓ Help": {
        "york?": "Show this help menu.",
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
            title=f"York — {category}",
            color=discord.Color.purple(),
        )
        for name, desc in cmds.items():
            embed.add_field(name=f"`{name}`", value=desc, inline=False)
        embed.set_footer(text="Satellite 06 — York (Greed) | Prefix: york")
        await interaction.response.edit_message(embed=embed)


class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(CategorySelect())


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="?")
    async def help_command(self, ctx):
        embed = discord.Embed(
            title="🍖 York — Satellite 06 (Greed)",
            description=(
                "...I'm busy. I need to eat, sleep, and accumulate things.\n"
                "But fine. Here. Pick a category.\n\n"
                "**Prefix:** `york`"
            ),
            color=discord.Color.purple(),
        )
        embed.set_footer(text="Use the menu below to explore commands.")
        await ctx.send(embed=embed, view=HelpView())


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
