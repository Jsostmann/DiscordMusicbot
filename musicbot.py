import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import utils
from musiccontroller import MusicController

load_dotenv()
DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().all()
bot = commands.Bot(command_prefix='-', intents=intents)

@bot.command(name='play', help='Play a song')
async def play(ctx, *, input):
    try :
        music_controller = MusicController.get_music_controller(ctx.message.guild)
        author = ctx.message.author

        if not music_controller.is_connected():
            await ctx.send("The bot is not connected to a voice channel.")
            return
        
        media_type = utils.is_spotify_input(input)
        if not media_type == utils.Spotify.UNKNOWN:
            if not utils.spotify_enabled():            
                await ctx.send("The bot is not setup to use spotify")
                return
            
            await music_controller.play_spotify(input, author)
            await ctx.send("Playing spotify playlist :scroll:")

        else:
            await music_controller.play_youtube(input, author)
            await ctx.send("Playing youtube song")
            #await ctx.send(embed=song.get_embed(music_controller.playlist.get_size()))

    except Exception as e:
        await ctx.send("Error playing song")
        print(e.with_traceback())


@bot.command(name='join', help='Tells the bot to join voice channel')
async def join(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)

    if music_controller.is_connected():
        await ctx.send("The bot is already connected to a channel")
        return
    else:
        channel_name = "music"
        await music_controller.connect(channel_name)


@bot.command(name='pause', help='Tells the bot to pause current song',aliases=['p'])
async def pause(ctx):

    music_controller = MusicController.get_music_controller(ctx.message.guild)
    if music_controller.is_playing():
        music_controller.pause()
        return
    await ctx.send("The bot is not playing anything at the moment.")
    

@bot.command(name='playlist', help="Tells the bot to show the current playlist", aliases=['pl'])
async def get_playlist(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)

    await ctx.send(embed= await music_controller.playlist.get_formatted_playlist())


@bot.command(name='skip', help='Tells the bot to sklip the current playlist', aliases=['fs'])
async def skip(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)

    if music_controller.is_playing():
        await music_controller.skip_song()
        await ctx.send("Skipped Song :track_next:")
        return
    
    await ctx.send("No song is playing to skip")


@bot.command(name='resume', help='Resumes the song', aliases=['r'])
async def resume(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)

    if music_controller.is_paused():
        music_controller.resume()
        return
    
    await ctx.send("The bot was not playing anything before this. Use play command")

@bot.command(name='song', help='Gives current song info', aliases=['s','c'])
async def song(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)

    if music_controller.is_playing():
        await ctx.send(embed=music_controller.playlist.playlist[0].get_embed(music_controller.playlist.get_size()))
        return
    
    await ctx.send("The bot is not playing anything")


@bot.command(name='leave', help='Tells the bot to leave its voice channel',aliases=['l'])
async def leave(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)

    if music_controller.is_connected():
        await music_controller.disconnect()
        return
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='stop', help='Tells the bot to stop the current song',aliases=['st'])
async def stop(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)

    if music_controller.is_playing():
        await music_controller.stop_playlist()
        return
    
    await ctx.send("The bot is not playing anything at the moment.")

@bot.command(name='loop', help='Tells the bot to loop the current song')
async def loop(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)

    if music_controller.is_playing():
        await music_controller.loop_song()
        return
    await ctx.send("The bot is not playing anything at the moment, cannot loop")


@bot.command(name='volume', help='Tells the bot to set its volume',aliases=['v'])
async def volume(ctx, *args):
    music_controller = MusicController.get_music_controller(ctx.message.guild)

    if not music_controller.is_connected():
        await ctx.send("The bot is not in a voice channel")
        return
    
    if not music_controller.is_playing():
        await ctx.send("The bot is not currently playing music")
        return
    try:  
        if len(args) == 0:         
            await ctx.send("Bots current volume :speaker: {}%".format(music_controller.get_volume()))
            return
        
        new_volume = int(args[0])
        success = music_controller.set_volume(new_volume)

        if success:
            await ctx.send("Set the bot's volume to :sound: {}%".format(music_controller.get_volume()))
            return

        await ctx.send("Please enter a value between [0,100]")

    except Exception as e:
        await ctx.send("Failed to set / get bot volume")
        print(e)


@bot.event
async def on_ready():
    print("Music Bot has started.")
    for guild in bot.guilds:
        await MusicController.register_guild(guild, bot)

@bot.event
async def on_guild_join(guild):
    print("New Guild joined.")
    await MusicController.register_guild(guild, bot)



if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)