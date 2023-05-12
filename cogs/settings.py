from discord.ext import commands
from guildmanager import GuildManager
from modules.decorators import *
import discord
from modules import utils
class Settings(commands.Cog, name="Settings"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='cooldown', help='Set the cooldown')
    @is_owner
    async def cooldown(self, ctx, *args):
        settings_controller = GuildManager.get_manager(ctx.guild).get_settings_controller()
        if len(args) < 1:
            await ctx.send("Must use argument **_true_**, **_false_** or **__/{cooldown period (s)/}")
            return
        await ctx.send("Must use argument **_true_**, **_false_** or **__/{cooldown period (s)/}__**")

    @commands.command(name='restart', help='Restart the bot', aliases=['rs'])
    @is_owner
    async def restart(self, ctx, *args):
        await ctx.send("Restarting the bot...")
        #os.execv(sys.executable, ['python'] + sys.argv)

    @commands.command(name='whitelist', help='Enable whitelist')
    @is_owner
    async def whitelist(self, ctx, *args):
        pass

    @commands.command(name='blacklist', help='Enable Blacklist')
    @is_owner
    async def blacklist(self, ctx, *args):
        pass

    @commands.command(name='test', help='test')
    @is_owner
    async def test(self, ctx, *args):
        embed = discord.Embed(description="test")
        #embed.set_author(name=f'{ctx.message.author.name} favorited a song', icon_url="https://raw.githubusercontent.com/Jsostmann/DiscordMusicbot/main/assets/emojis/cd_spin_emoji.GIF")
        #embed.set_image(url='https://raw.githubusercontent.com/Jsostmann/DiscordMusicbot/main/assets/emojis/favorite.png')
        #file = utils.embed_local_image(embed, f"{input}.png", "author")
        #await ctx.send(embed=embed, file=file)

async def setup(bot):
    await bot.add_cog(Settings(bot))