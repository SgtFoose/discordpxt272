import os
import discord
from discord.ext import commands
from discord import ui, Interaction

# Optional: Import keep-alive for 24/7 hosting
try:
    from keep_alive import keep_alive
    keep_alive()
except ImportError:
    print("ℹ️ Keep-alive not available (optional)")

# Get bot token from environment variable for secure deployment
BOT_TOKEN = os.getenv("DISCORD_TOKEN")

if not BOT_TOKEN:
    print("❌ Error: DISCORD_TOKEN environment variable not set!")
    exit(1)

# Enhanced bot with Bear Hunt Rally Calculator
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 {bot.user} has logged in!")
    print("🐻 Bear Hunt Rally Calculator ready for deployment!")

# Super simple test commands
@bot.command()
async def alive(ctx):
    """Super simple alive check"""
    await ctx.send("🟢 Bot is alive!")

@bot.command()
async def test(ctx):
    """Simple test command"""
    await ctx.send("✅ Bot is working! All systems operational. 🚀")

if __name__ == "__main__":
    print("🚀 Starting Bear Hunt Rally Calculator for deployment...")
    bot.run(BOT_TOKEN)