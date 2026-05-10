import random
import discord
from discord.ext import commands, tasks
import shared_db

HUNGER_MESSAGES = {
    "critical": [
        "I'm STARVING!! Someone feed me RIGHT NOW or I'm going to cause problems!! 😤🍖",
        "HUNGER LEVEL CRITICAL. Basic needs: UNFULFILLED. This is unacceptable. Feed me. 😤",
        "I haven't eaten in forever. This is NOT okay. My biological functions demand sustenance. 🍖",
    ],
    "low": [
        "...I'm a little hungry. Just a little. Feed me if you want. (I do want.) 🍖",
        "My hunger subroutine is triggering. Someone bring food. Please. 😕",
        "Hey. York here. Hungry. Someone feed me. That's all. 🍓",
    ],
    "medium": [
        "I'm getting peckish. It would be nice if someone fed me soon... 🍖",
        "Hunger alert. Nothing urgent, but I'd appreciate a snack. 😌",
    ],
}

FEED_RESPONSES = [
    "Mmm... that was exactly what I needed. Thank you. (I won't say it twice.)",
    "...Acceptable. My hunger has decreased. You have earned my acknowledgment.",
    "Good. Very good. I feel my basic needs being met. This is all I require.",
    "Delicious. You may continue to exist in my good graces.",
    "My biological functions are restored. Temporarily. Feed me again soon.",
]

TRUST_MILESTONES = {
    100:  "York nods at you. *\"You're... acceptable.\"*",
    300:  "York looks at you. *\"...Friend. I suppose.\"*",
    700:  "York smiles slightly. *\"Close friend. Don't make it weird.\"*",
    1500: "York stares at you for a long moment. *\"I trust you. Completely. This is rare.\"*",
}


class FeedView(discord.ui.View):
    def __init__(self, guild_id: int):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.feeders = set()

    @discord.ui.button(label="Feed York 🍖  (FREE — earn bounty!)", style=discord.ButtonStyle.primary)
    async def feed_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        guild_id = self.guild_id

        if user_id in self.feeders:
            await interaction.response.send_message(
                "...You already fed me this time. Don't be greedy. Wait for the next alert. 😒",
                ephemeral=True,
            )
            return

        old_trust = shared_db.get_trust(user_id, guild_id)
        old_level, _, _ = shared_db.get_trust_level(old_trust)

        # Bounty reward scales with trust level
        BOUNTY_BY_LEVEL = {0: 25, 1: 40, 2: 60, 3: 85, 4: 120}
        bounty = BOUNTY_BY_LEVEL[old_level]

        shared_db.add_berries(user_id, guild_id, bounty, reason="Bounty for feeding York")
        shared_db.add_trust(user_id, guild_id, 20)
        shared_db.feed_york(guild_id, user_id)
        self.feeders.add(user_id)

        new_trust = shared_db.get_trust(user_id, guild_id)
        _, label, _ = shared_db.get_trust_level(new_trust)

        state = shared_db.get_york_state(guild_id)
        hunger = state[0]

        response_msg = random.choice(FEED_RESPONSES)
        embed = discord.Embed(
            title="🍖 York has been fed!",
            description=f"{interaction.user.mention} fed York!\n\n*\"{response_msg}\"*",
            color=discord.Color.purple(),
        )
        embed.add_field(name="🍓 Bounty Earned", value=f"+{bounty} berries", inline=True)
        embed.add_field(name="💜 Trust Gained", value="+20 pts", inline=True)
        embed.add_field(name="🍖 York's Hunger", value=f"{hunger}/100", inline=True)
        embed.add_field(name="Trust Level", value=f"**{label}** ({new_trust} pts)", inline=True)

        milestone_msg = None
        for threshold, msg in TRUST_MILESTONES.items():
            if old_trust < threshold <= new_trust:
                milestone_msg = msg
                break

        if milestone_msg:
            embed.add_field(name="🎉 Trust Milestone!", value=milestone_msg, inline=False)

        await interaction.response.send_message(embed=embed)


class HungerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hunger_decay.start()

    def cog_unload(self):
        self.hunger_decay.cancel()

    @tasks.loop(minutes=30)
    async def hunger_decay(self):
        for guild in self.bot.guilds:
            state = shared_db.get_york_state(guild.id)
            if not state:
                continue
            hunger_level, last_fed, channel_id = state
            if not channel_id:
                continue

            channel = guild.get_channel(int(channel_id))
            if not channel:
                continue

            prev = hunger_level
            new_hunger = max(0, hunger_level - 15)
            shared_db.update_york_hunger(guild.id, new_hunger)

            if new_hunger <= 25 and prev > 25:
                msg = random.choice(HUNGER_MESSAGES["critical"])
                await self._send_hunger_alert(channel, guild.id, new_hunger, msg, urgent=True)
            elif new_hunger <= 50 and prev > 50:
                msg = random.choice(HUNGER_MESSAGES["low"])
                await self._send_hunger_alert(channel, guild.id, new_hunger, msg, urgent=False)
            elif new_hunger <= 75 and prev > 75:
                msg = random.choice(HUNGER_MESSAGES["medium"])
                await self._send_hunger_alert(channel, guild.id, new_hunger, msg, urgent=False)

    @hunger_decay.before_loop
    async def before_decay(self):
        await self.bot.wait_until_ready()

    async def _send_hunger_alert(self, channel, guild_id, hunger, message, urgent=False):
        color = discord.Color.red() if urgent else discord.Color.orange()
        bar_filled = int(hunger / 10)
        bar = "🟪" * bar_filled + "⬛" * (10 - bar_filled)
        embed = discord.Embed(
            title="🍖 York is Hungry!" if not urgent else "🚨 York is STARVING!",
            description=message,
            color=color,
        )
        embed.add_field(name="Hunger Level", value=f"`{bar}` {hunger}/100", inline=False)
        embed.add_field(name="Cost to Feed", value="FREE 🆓", inline=True)
        embed.add_field(name="Reward", value="Bounty 🍓 + Trust 💜", inline=True)
        embed.set_footer(text="Satellite 06 — York (Greed) | Punk Records System")
        view = FeedView(guild_id=guild_id)
        await channel.send(embed=embed, view=view)

    @commands.command(name="status")
    async def status(self, ctx):
        state = shared_db.get_york_state(ctx.guild.id)
        hunger, last_fed, channel_id = state
        bar_filled = int(hunger / 10)
        bar = "🟪" * bar_filled + "⬛" * (10 - bar_filled)
        if hunger > 75:
            mood = "😊 Content"
        elif hunger > 50:
            mood = "😐 Getting Hungry"
        elif hunger > 25:
            mood = "😕 Hungry"
        else:
            mood = "😤 STARVING"
        embed = discord.Embed(
            title="🍖 York's Status",
            color=discord.Color.purple(),
        )
        embed.add_field(name="Hunger Level", value=f"`{bar}` **{hunger}/100**", inline=False)
        embed.add_field(name="Mood", value=mood, inline=True)
        embed.add_field(name="Last Fed", value=last_fed[:16] if last_fed else "Never", inline=True)
        embed.add_field(name="Alert Channel", value=f"<#{channel_id}>" if channel_id else "Not set — use `york setchannel`", inline=False)
        embed.set_footer(text="Satellite 06 — York (Greed)")
        await ctx.send(embed=embed)

    @commands.command(name="trust")
    async def trust(self, ctx, member: discord.Member = None):
        target = member or ctx.author
        trust = shared_db.get_trust(target.id, ctx.guild.id)
        level, label, multiplier = shared_db.get_trust_level(trust)
        thresholds = [0, 100, 300, 700, 1500]
        next_t = thresholds[level + 1] if level < 4 else None
        bar_filled = min(10, int((trust / (next_t or 1500)) * 10)) if next_t else 10
        bar = "💜" * bar_filled + "░" * (10 - bar_filled)
        embed = discord.Embed(
            title=f"💜 York Trust — {target.display_name}",
            color=discord.Color.purple(),
        )
        embed.add_field(name="Trust Points", value=f"**{trust}**", inline=True)
        embed.add_field(name="Trust Level", value=f"**{label}** (Lv.{level})", inline=True)
        embed.add_field(name="Progress", value=f"`{bar}`\n{'Next: ' + str(next_t - trust) + ' pts away' if next_t else '**MAX LEVEL**'}", inline=False)
        embed.set_footer(text="Feed York to gain trust | Satellite 06")
        await ctx.send(embed=embed)

    @commands.command(name="perks")
    async def perks(self, ctx):
        embed = discord.Embed(
            title="💜 York Trust Level Perks",
            description="Feed York to build trust and unlock rewards across all satellites.",
            color=discord.Color.purple(),
        )
        perks_data = [
            ("Lv.0 — Stranger",    "0 pts",    "Feed bounty: **25 🍓** • No daily multiplier bonus"),
            ("Lv.1 — Acquaintance","100 pts",  "Feed bounty: **40 🍓** • +10% daily berry multiplier"),
            ("Lv.2 — Friend",      "300 pts",  "Feed bounty: **60 🍓** • +20% daily berry multiplier"),
            ("Lv.3 — Close Friend","700 pts",  "Feed bounty: **85 🍓** • +30% daily berry multiplier"),
            ("Lv.4 — Trusted",     "1500 pts", "Feed bounty: **120 🍓** • +50% daily berry multiplier • Max bonuses"),
        ]
        for name, req, desc in perks_data:
            embed.add_field(name=f"{name} ({req})", value=desc, inline=False)
        embed.set_footer(text="Satellite 06 — York (Greed)")
        await ctx.send(embed=embed)

    @commands.command(name="setchannel")
    @commands.has_permissions(manage_channels=True)
    async def setchannel(self, ctx, channel: discord.TextChannel = None):
        target = channel or ctx.channel
        shared_db.set_york_channel(ctx.guild.id, target.id)
        embed = discord.Embed(
            title="✅ Hunger Alert Channel Set",
            description=f"York will post hunger alerts in {target.mention}.",
            color=discord.Color.purple(),
        )
        embed.set_footer(text="Satellite 06 — York (Greed)")
        await ctx.send(embed=embed)

    @commands.command(name="feed")
    async def feed(self, ctx):
        state = shared_db.get_york_state(ctx.guild.id)
        hunger = state[0]
        bar_filled = int(hunger / 10)
        bar = "🟪" * bar_filled + "⬛" * (10 - bar_filled)
        embed = discord.Embed(
            title="🍖 York is waiting...",
            description=f"*\"Feed me if you want. I won't beg. (Feed me.)\"*",
            color=discord.Color.purple(),
        )
        embed.add_field(name="Hunger Level", value=f"`{bar}` {hunger}/100", inline=False)
        embed.add_field(name="Cost", value="FREE 🆓", inline=True)
        embed.add_field(name="Reward", value="Bounty 🍓 + Trust 💜", inline=True)
        embed.set_footer(text="Satellite 06 — York (Greed)")
        view = FeedView(guild_id=ctx.guild.id)
        await ctx.send(embed=embed, view=view)


async def setup(bot):
    await bot.add_cog(HungerCog(bot))
