import sys
sys.dont_write_bytecode = True

import discord
from discord.ext import commands
from guildmanager import GuildManager
import utils

class Settings(commands.Cog, name="Settings"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cooldown', help='set the cooldown', aliases=['cd'])
    async def cooldown(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_settings_controller()
        pass


async def setup(bot):
    await bot.add_cog(Settings(bot))