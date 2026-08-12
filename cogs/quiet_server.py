import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import random


class QuietServer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.quiet_minutes = 30

        # Each server gets its own last-message timestamp
        self.last_message = {}

        # Prevent repeated messages per server
        self.triggered = set()

        self.check_quiet.start()

    def cog_unload(self):
        self.check_quiet.cancel()

    @commands.Cog.listener()
    async def on_message(self, message):

        # Ignore DMs
        if message.guild is None:
            return

        # Ignore bots
        if message.author.bot:
            return

        guild_id = message.guild.id

        # Reset this server's quiet timer
        self.last_message[guild_id] = datetime.now()

        # Allow York to trigger again
        self.triggered.discard(guild_id)

    @tasks.loop(seconds=30)
    async def check_quiet(self):

        now = datetime.now()

        for guild in self.bot.guilds:

            guild_id = guild.id

            # If York hasn't seen a message from this server yet
            if guild_id not in self.last_message:
                self.last_message[guild_id] = now
                continue

            quiet_for = now - self.last_message[guild_id]

            if quiet_for < timedelta(minutes=self.quiet_minutes):
                continue

            # Already triggered for this quiet period
            if guild_id in self.triggered:
                continue

            self.triggered.add(guild_id)

            messages = [
                "👀 It's awfully quiet in here...",
                "🏴‍☠️ Did everyone abandon the ship?",
                "🍽️ York is beginning to question whether anyone actually lives here.",
                "📡 Den Den Mushi reports... absolutely nothing.",
                "🌊 The sea is strangely calm today...",
                "🚨 SERVER ACTIVITY LEVEL: CONCERNINGLY LOW."
            ]

            text = random.choice(messages)

            # Find a channel York can send in
            channel = discord.utils.find(
                lambda c:
                    isinstance(c, discord.TextChannel)
                    and c.permissions_for(guild.me).send_messages,
                guild.text_channels
            )

            if channel:
                await channel.send(text)


async def setup(bot):
    await bot.add_cog(QuietServer(bot))
