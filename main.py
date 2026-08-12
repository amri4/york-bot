import os
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv
import mycord

intents = discord.Intents.default()
intents.message_content = True  

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_extensions():
    print("📂 Scanning for cogs...")
    if os.path.exists("./cogs"):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                try:
                    await bot.load_extension(f"cogs.{filename[:-3]}")
                    print(f"  └─ Loaded cog: {filename}")
                except Exception as e:
                    print(f"  ❌ Failed to load cog {filename}: {e}")
    else:
        print("⚠️ No 'cogs' folder found.")

@bot.event
async def on_ready():
    print(f"🤖 Success! Logged in as {bot.user.name}")
    print("⚡ Bot is online and listening.")

async def main():
    await load_extensions()
    
    # Grab the token from the environment securely
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        print("❌ CRITICAL ERROR: 'DISCORD_TOKEN' environment variable is missing!")
        print("Please add it to your MonkeyBytes panel variables or your local .env file.")
        return

    await bot.start(token)

asyncio.run(main())
