import os
import sys
from discord.ext import commands
from guildmanager import GuildManager
import modules.utils as utils
import modules.database as db
from modules.decorators import *

class Settings(commands.Cog, name="Settings"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cooldown', help='Set the cooldown', aliases=['cd'])
    @is_owner
    async def cooldown(self, ctx):
        settings_controller = GuildManager.get_manager(ctx.guild).get_settings_controller()
    
    @commands.command(name='restart', help='Restart the bot', aliases=['rs'])
    @check_cooldown
    async def restart(self, ctx):
        await ctx.send("Restarting the bot...")
        await db.get_users_in_guild(ctx.guild.id)
        #os.execv(sys.executable, ['python'] + sys.argv)


async def setup(bot):
    await bot.add_cog(Settings(bot))