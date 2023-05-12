from discord.ext import commands
from guildmanager import GuildManager
import modules.utils as utils
import modules.database as db
from modules.decorators import *

class User(commands.Cog, name="User"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='save_song', help='Saves song to database')
    async def save_song(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

        if not music_controller.is_playing():
            await ctx.send("No song playing, can't save song")
            return
        
        song = music_controller.current_song
        res = await db.favorite_song(ctx.guild.id, ctx.message.author.id, song)

        if res:
            await ctx.send("Already Saved this song")
            return
        
        await ctx.send("Successfully saved song")

    @commands.command(name='show_song', help='Show user saved songs')
    async def show_song(self, ctx, *nums):
        if len(nums) < 1:
            await ctx.send("Must use argument **_all_** or **_server_**")
            return
        show_type = nums[0]

        match show_type:
            case "all":
                #show all saved songs
                pass
            case "server":
                pass
                #show server specific saved songs
            case _:
                #unknown argument
                pass
        await db.join("t","t")

    @commands.command(name='show_playlists', help='Show user playlists')
    async def show_playlist(self, ctx):
        res = await db.get_user_playlists(ctx.guild.id, ctx.message.author.id)

        if res:
            await ctx.send(str(res))
            return
        
        await ctx.send("Created new playlist")

    @commands.command(name='create_playlist', help='Create user playlist')
    async def create_playlist(self, ctx, playlist_name):
        res = await db.create_user_playlist(ctx.guild.id, ctx.message.author.id, playlist_name)

        if res:
            await ctx.send("Already created playlist")
            return
        
        await ctx.send("Created new playlist")



async def setup(bot):
    await bot.add_cog(User(bot))