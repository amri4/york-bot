import discord
from discord.ext import commands
import os
from backup import backup

bot = commands.Bot(command_prefix="Shaka ", intents=discord.Intents.default())

@bot.event
async def on_ready():
    print("Shaka online 🧠")

@bot.command()
async def status(ctx):
    await ctx.send("Shaka is online 🧠")

@bot.command()
async def backup_cmd(ctx):
    backup()
    await ctx.send("Backup done 🧬")

bot.run(os.getenv("TOKEN"))
