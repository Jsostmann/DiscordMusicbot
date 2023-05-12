import discord
from discord.ext import commands
from guildmanager import GuildManager
import modules.utils as utils

class Music(commands.Cog, name="Music"):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='play', help='Play a song')
    async def play(self, ctx, *, input):
        try :
            music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()
            
            author = ctx.message.author

            if not music_controller.is_connected():
                await ctx.send("The bot is not connected to a voice channel.")
                return
            
            media_type = utils.is_spotify_input(input)
            if not media_type == utils.Spotify.UNKNOWN:
                if not utils.spotify_enabled():            
                    await ctx.send(f"{utils.emoji_map['spotify_emoji']} The bot is not setup to use spotify")
                    return
                t = music_controller.play_spotify(input, author)
                await ctx.send(f"Playing spotify playlist {utils.emoji_map['spotify_emoji']}")
                await t
            else:
                song = await music_controller.play_youtube(input, author)
                await ctx.send(f"{utils.emoji_map['youtube_emoji']} Playing youtube song")
                await ctx.send(embed=song.get_embed(pos=music_controller.playlist.get_size(),type="song"))

        except Exception as e:
            await ctx.send("Error playing song")
            print(e.with_traceback())

    @commands.command(name='join', help='Tells the bot to join voice channel', aliases=['j'])
    async def join(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

        if music_controller.is_connected():
            await ctx.send("The bot is already connected to a channel")
            return
        else:
            channel_name = "music"
            await music_controller.connect(channel_name)


    @commands.command(name='pause', help='Tells the bot to pause current song', aliases=['p'])
    async def pause(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

        if music_controller.is_playing():
            music_controller.pause()
            await ctx.send(embed=discord.Embed(description="**:pause_button: Paused Song**"))
            return
        await ctx.send("The bot is not playing anything at the moment.")
        

    @commands.command(name='playlist', help="Tells the bot to show the current playlist", aliases=['pl'])
    async def get_playlist(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

        await ctx.send(embed= await music_controller.playlist.get_formatted_playlist())


    @commands.command(name='skip', help='Tells the bot to sklip the current playlist', aliases=['fs'])
    async def skip(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

        if music_controller.is_playing():
            await music_controller.skip_song()
            await ctx.send(embed=discord.Embed(description="**Skipped Song :track_next:**"))
            return
        
        await ctx.send("No song is playing to skip")


    @commands.command(name='resume', help='Resumes the song', aliases=['r'])
    async def resume(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

        if music_controller.can_resume():
            music_controller.resume()
            embed = discord.Embed(description="**:arrow_forward: Resumed Song**")
            await ctx.send(embed=embed)
            return
        
        await ctx.send("The bot was not playing anything before this. Use play command")


    @commands.command(name='song', help='Gives current song info', aliases=['s','c'])
    async def song(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

        if music_controller.is_playing():
            await ctx.send(embed=await music_controller.get_current_song())
            return
        
        await ctx.send("The bot is not playing anything")


    @commands.command(name='shuffle', help='Shuffles the playlist', aliases=['sh'])
    async def shuffle(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

        if music_controller.playlist_is_empty():
            await ctx.send("Cant shuffle, playlist is empty")
            return
        
        if music_controller.get_playlist_size() < 3:
            await ctx.send(f"Cant shuffle, only {music_controller.get_playlist_size()} song in playlist")
            return

        await music_controller.shuffle_playlist()
        embed = discord.Embed(description="**Shuffled playlist :twisted_rightwards_arrows:**")
        await ctx.send(embed=embed)


    @commands.command(name='leave', help='Tells the bot to leave its voice channel', aliases=['l'])
    async def leave(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

        if music_controller.is_connected():
            await music_controller.disconnect()
            return
        else:
            await ctx.send("The bot is not connected to a voice channel.")


    @commands.command(name='stop', help='Tells the bot to stop the current song', aliases=['st'])
    async def stop(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

        if music_controller.is_playing():
            await music_controller.stop_playlist()
            return
        
        await ctx.send("The bot is not playing anything at the moment.")


    @commands.command(name='loop_song', help='Tells the bot to loop the current song', aliases=['ls'])
    async def loop_song(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()
    
        if not music_controller.is_playing():
            await ctx.send("The bot is not playing anything at the moment, cannot loop song")
            return
        
        if not music_controller.is_song_looping():
            await ctx.send(embed=discord.Embed(description="**Loop song enabled :repeat:**"))
        else:
            await ctx.send(embed=discord.Embed(description="**Loop song disabled :white_check_mark:**"))

        await music_controller.loop_song()


    @commands.command(name='loop_playlist', help='Tells the bot to loop the playlist', aliases=['lp'])
    async def loops(self, ctx):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()
    
        if not music_controller.is_playing():
            await ctx.send("The bot is not playing anything at the moment, cannot loop playlist")
            return
        
        if not music_controller.is_playlist_looping():
            await ctx.send(embed=discord.Embed(description="**Loop playlist enabled :repeat:**"))
        else:
            await ctx.send(embed=discord.Embed(description="**Looping playlist disabled :white_check_mark:**"))

        await music_controller.loop_playlist()


    @commands.command(name='volume', help='Tells the bot to set its volume', aliases=['v'])
    async def volume(self, ctx, *args):
        music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

        if not music_controller.is_connected():
            await ctx.send("The bot is not in a voice channel")
            return
        
        if not music_controller.is_playing():
            await ctx.send("The bot is not currently playing music")
            return
        try:  
            if len(args) == 0:         
                await ctx.send(embed=discord.Embed(description=f"**Bots current volume :speaker: {music_controller.get_volume()}%**"))
                return
            
            new_volume = int(args[0])
            success = music_controller.set_volume(new_volume)

            if success:
                await ctx.send(embed=discord.Embed(description=f"**Set the bot's volume to :sound: {music_controller.get_volume()}%**"))
                return

            await ctx.send("Please enter a value between [0,100]")

        except Exception as e:
            await ctx.send("Failed to set / get bot volume")
            print(e)
            print(type(e).__name__)

    
async def setup(bot):
    await bot.add_cog(Music(bot))
