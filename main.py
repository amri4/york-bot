import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
import database

load_dotenv()

SIBLING_NAMES = ["Shaka", "Lilith", "Edison", "Pythagoras", "Atlas"]

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=["york ", "york", "York ", "York"], intents=intents, help_command=None)


@bot.event
async def on_ready():
    database.init_db()
    await bot.load_extension("cogs.help_command")
    await bot.load_extension("cogs.greed")
    print(f"[York] Online as {bot.user} (ID: {bot.user.id})")
    print(f"[York] Prefix: york | Satellite 06 — Greed")


@bot.event
async def on_message(message):
    if message.author.bot:
        return

    content_lower = message.content.lower()
    for name in SIBLING_NAMES:
        if name.lower() in content_lower:
            responses = [
                f"...{name}? I'm busy. I need to eat and sleep. Don't bother me with their name.",
                f"{name} has nothing I want. Almost nothing.",
                f"Hmm. {name}. They have resources I could use. Noted.",
            ]
            await message.channel.send(random.choice(responses))
            break

    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    raise error


if __name__ == "__main__":
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_TOKEN not set in .env")
    bot.run(token)
