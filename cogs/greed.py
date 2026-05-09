import random
import discord
from discord.ext import commands
import database

SLEEP_DURATIONS = [
    "8 hours and 47 minutes. Exactly optimal.",
    "just 12 minutes. I was tired, not lazy.",
    "a full 10 hours. Basic needs fulfilled.",
    "3 hours. Insufficient. I'll nap again later.",
    "6 hours and 23 minutes. My body required it.",
    "until noon. It was necessary for recovery.",
    "the whole afternoon. Don't judge me.",
]

SLEEP_QUOTES = [
    "Sleep is a basic need. I require it.",
    "I'm not lazy. I'm replenishing my energy reserves.",
    "Even Stella needs rest. This is science.",
    "Properly rested York is more productive York.",
    "Dreams? I dreamed about food. Obviously.",
]

CLAIM_RESPONSES = [
    "It's mine now. Don't touch it.",
    "Claimed. I'll be keeping this indefinitely.",
    "This is York's property now. I'll hear no arguments.",
    "Filed under: Mine. Category: All of it.",
    "Acquired. Thank you for your service.",
]

SIBLINGS = [
    ("Shaka", "01", "Good", "shaka"),
    ("Lilith", "02", "Evil", "lilith"),
    ("Edison", "03", "Thinker", "edison"),
    ("Pythagoras", "04", "Wisdom", "py"),
    ("Atlas", "05", "Violence", "atlas"),
    ("York", "06", "Greed", "york"),
]


class GreedCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="eat")
    async def eat(self, ctx, *, food: str):
        database.add_meal(ctx.guild.id, ctx.author.id, food)
        embed = discord.Embed(
            title="🍖 York Eats",
            description=f"*York consumes **{food}** without offering anyone else any.*",
            color=discord.Color.purple(),
        )
        embed.set_footer(text="Basic needs fulfilled. | Satellite 06 — York (Greed)")
        await ctx.send(embed=embed)

    @commands.command(name="sleep")
    async def sleep(self, ctx):
        duration = random.choice(SLEEP_DURATIONS)
        quote = random.choice(SLEEP_QUOTES)
        embed = discord.Embed(
            title="💤 York is Sleeping",
            description=f"*York sleeps for {duration}*\n\n*\"{quote}\"*",
            color=discord.Color.purple(),
        )
        embed.set_footer(text="Satellite 06 — York (Greed) | Do not disturb.")
        await ctx.send(embed=embed)

    @commands.command(name="claim")
    async def claim(self, ctx, *, item: str):
        database.add_claimed_item(ctx.guild.id, item)
        response = random.choice(CLAIM_RESPONSES)
        embed = discord.Embed(
            title="📦 Item Claimed",
            description=f"**{item}** — {response}",
            color=discord.Color.purple(),
        )
        embed.set_footer(text="Satellite 06 — York (Greed)")
        await ctx.send(embed=embed)

    @commands.command(name="inventory")
    async def inventory(self, ctx):
        rows = database.get_claimed_items(ctx.guild.id)
        if not rows:
            await ctx.send("Nothing claimed yet. Use `york claim <item>` to stake your claim.")
            return
        embed = discord.Embed(
            title="📦 York's Claimed Items",
            description="Everything here belongs to York. All of it.",
            color=discord.Color.purple(),
        )
        for item, timestamp in rows:
            embed.add_field(name=item, value=f"Claimed on {timestamp[:10]}", inline=False)
        embed.set_footer(text="Satellite 06 — York (Greed)")
        await ctx.send(embed=embed)

    @commands.command(name="take")
    async def take(self, ctx, member: discord.Member, amount: int):
        if amount <= 0:
            await ctx.send("The amount must be greater than 0. I don't give things back.")
            return
        if member.id == ctx.author.id:
            await ctx.send("Taking from myself? That makes no sense even to me.")
            return
        if member.bot:
            await ctx.send("Bots have no coins worth taking.")
            return
        database.add_taken_coins(ctx.guild.id, ctx.author.id, member.id, amount)
        embed = discord.Embed(
            title="💰 Coins Taken",
            description=f"York takes **{amount} coins** from {member.mention}. For herself, naturally.",
            color=discord.Color.purple(),
        )
        embed.set_footer(text="Satellite 06 — York (Greed)")
        await ctx.send(embed=embed)

    @commands.command(name="wallet")
    async def wallet(self, ctx):
        total = database.get_total_taken(ctx.guild.id, ctx.author.id)
        meals = database.get_recent_meals(ctx.guild.id, limit=3)
        embed = discord.Embed(
            title="💰 York's Wallet",
            color=discord.Color.purple(),
        )
        embed.add_field(name="Total coins taken", value=f"**{total}**", inline=False)
        if meals:
            meal_list = "\n".join([f"• {food} (by <@{uid}>)" for uid, food, _ in meals])
            embed.add_field(name="Recent meals", value=meal_list, inline=False)
        embed.set_footer(text="Satellite 06 — York (Greed)")
        await ctx.send(embed=embed)

    @commands.command(name="siblings")
    async def siblings(self, ctx):
        embed = discord.Embed(
            title="🤖 The Six Vegapunk Satellites",
            description="The others. They have things I want.",
            color=discord.Color.purple(),
        )
        for name, number, trait, prefix in SIBLINGS:
            marker = " ← you are here" if name == "York" else ""
            embed.add_field(
                name=f"Satellite {number} — {name} ({trait}){marker}",
                value=f"Prefix: `{prefix}`",
                inline=False,
            )
        await ctx.send(embed=embed)

    @eat.error
    async def eat_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `york eat <food>`")

    @claim.error
    async def claim_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `york claim <item>`")

    @take.error
    async def take_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Usage: `york take @user <amount>`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("The amount must be a number. `york take @user <amount>`")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("I can't take from someone who doesn't exist.")


async def setup(bot):
    await bot.add_cog(GreedCog(bot))
