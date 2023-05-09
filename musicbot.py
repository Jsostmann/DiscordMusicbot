import sys
sys.dont_write_bytecode = True

import discord
import asyncio
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
from guildmanager import GuildManager
import modules.database as db

load_dotenv()
DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='-', intents=intents)

@bot.event
async def on_ready():
    print("Music Bot has started.")
    await db.init_guilds(bot.guilds)
    await db.init_guild_members(bot.guilds)
    presence_task.start()
    for guild in bot.guilds:
        await GuildManager.register_guild(guild, bot)

@bot.event
async def on_guild_join(guild):
    print("New Guild joined.")
    await GuildManager.register_guild(guild, bot)

@tasks.loop(seconds=30)
async def presence_task():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name=f"on {len(bot.guilds)} servers"))

async def load_cogs():
    for file in os.listdir(os.path.join("cogs")):
        if not file.endswith(".py"):
            continue
        cog_name = file[:-3]
        try:
            await bot.load_extension(f"cogs.{cog_name}")
        except Exception as e:
            exception = f"{type(e).__name__}: {e}"
            print(exception)

if __name__ == "__main__" :
    asyncio.run(load_cogs())
    asyncio.run(db.init_db())
    bot.run(DISCORD_TOKEN, reconnect=True)