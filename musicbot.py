import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import utils
from guildmanager import GuildManager

load_dotenv()
DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='-', intents=intents)


@bot.command(name='play', help='Play a song')
async def play(ctx, *, input):
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
            await ctx.send(f"Playing spotify playlist {utils.emoji_map['playlist']}")
            await t
        else:
            song = await music_controller.play_youtube(input, author)
            await ctx.send(f"{utils.emoji_map['youtube_emoji']} Playing youtube song")
            await ctx.send(embed=song.get_embed(pos=music_controller.playlist.get_size(),type="song"))

    except Exception as e:
        await ctx.send("Error playing song")
        print(e.with_traceback())


@bot.command(name='join', help='Tells the bot to join voice channel', aliases=['j'])
async def join(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

    if music_controller.is_connected():
        await ctx.send("The bot is already connected to a channel")
        return
    else:
        channel_name = "music"
        await music_controller.connect(channel_name)


@bot.command(name='pause', help='Tells the bot to pause current song', aliases=['p'])
async def pause(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

    if music_controller.is_playing():
        music_controller.pause()
        await ctx.send(embed=discord.Embed(description="**:pause_button: Paused Song**"))
        return
    await ctx.send("The bot is not playing anything at the moment.")
    

@bot.command(name='playlist', help="Tells the bot to show the current playlist", aliases=['pl'])
async def get_playlist(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

    await ctx.send(embed= await music_controller.playlist.get_formatted_playlist())


@bot.command(name='skip', help='Tells the bot to sklip the current playlist', aliases=['fs'])
async def skip(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

    if music_controller.is_playing():
        await music_controller.skip_song()
        await ctx.send(embed=discord.Embed(description="**Skipped Song :track_next:**"))
        return
    
    await ctx.send("No song is playing to skip")


@bot.command(name='resume', help='Resumes the song', aliases=['r'])
async def resume(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

    if music_controller.can_resume():
        music_controller.resume()
        embed = discord.Embed(description="**:arrow_forward: Resumed Song**")
        await ctx.send(embed=embed)
        return
    
    await ctx.send("The bot was not playing anything before this. Use play command")


@bot.command(name='song', help='Gives current song info', aliases=['s','c'])
async def song(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

    if music_controller.is_playing():
        await ctx.send(embed=await music_controller.get_current_song())
        return
    
    await ctx.send("The bot is not playing anything")


@bot.command(name='shuffle', help='Shuffles the playlist', aliases=['sh'])
async def shuffle(ctx):
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


@bot.command(name='leave', help='Tells the bot to leave its voice channel', aliases=['l'])
async def leave(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

    if music_controller.is_connected():
        await music_controller.disconnect()
        return
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='stop', help='Tells the bot to stop the current song', aliases=['st'])
async def stop(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

    if music_controller.is_playing():
        await music_controller.stop_playlist()
        return
    
    await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name='loop_song', help='Tells the bot to loop the current song', aliases=['ls'])
async def loop_song(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()
 
    if not music_controller.is_playing():
        await ctx.send("The bot is not playing anything at the moment, cannot loop song")
        return
    
    if not music_controller.is_song_looping():
        await ctx.send(embed=discord.Embed(description="**Loop song enabled :repeat:**"))
    else:
        await ctx.send(embed=discord.Embed(description="**Loop song disabled :white_check_mark:**"))

    await music_controller.loop_song()


@bot.command(name='loop_playlist', help='Tells the bot to loop the playlist', aliases=['lp'])
async def loops(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()
 
    if not music_controller.is_playing():
        await ctx.send("The bot is not playing anything at the moment, cannot loop playlist")
        return
    
    if not music_controller.is_playlist_looping():
        await ctx.send(embed=discord.Embed(description="**Loop playlist enabled :repeat:**"))
    else:
        await ctx.send(embed=discord.Embed(description="**Looping playlist disabled :white_check_mark:**"))

    await music_controller.loop_playlist()


@bot.command(name='volume', help='Tells the bot to set its volume', aliases=['v'])
async def volume(ctx, *args):
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


@bot.event
async def on_ready():
    print("Music Bot has started.")
    update_presence.start()
    for guild in bot.guilds:
        await GuildManager.register_guild(guild, bot)

@bot.event
async def on_guild_join(guild):
    print("New Guild joined.")
    await GuildManager.register_guild(guild, bot)

@tasks.loop(seconds=30)
async def update_presence():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Music Bot", details="-help for command help", state="playing music.."))


if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN, reconnect=True)