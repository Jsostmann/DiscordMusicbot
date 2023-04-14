import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import yt_dlp as yt_dl
from song import Song
import utils
from musiccontroller import MusicController

load_dotenv()
DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='-', intents=intents)

@bot.command(name='play', help='Play a song')
async def play(ctx, *, url):
    try :
        music_controller = MusicController.get_music_controller(ctx.message.guild)
        author = ctx.message.author

        if not music_controller.is_connected():
            await ctx.send("The bot is not connected to a voice channel.")
            return

        song_url = utils.search_youtube(url)
        downloader = yt_dl.YoutubeDL(utils.YT_DL_OPTIONS)
        
        result_map = downloader.extract_info(song_url, download=False)
        result_map.update({"requestee": author})
        song = Song(result_map)

        async with ctx.typing():
            music_controller.process_song(song)
            await ctx.send(embed=song.get_embed(music_controller.playlist.get_size() + 1))

    except Exception as e:
        await ctx.send("Error playing song")
        print(e.with_traceback())


@bot.command(name='join', help='Tells the bot to join voice channel')
async def join(ctx):
        music_controller = MusicController.get_music_controller(ctx.message.guild)

        if music_controller.is_connected():
            await ctx.send("The bot is already connected to a channel")
            return
        channel_name = "music"
        await music_controller.connect(channel_name)


@bot.command(name='pause', help='Tells the bot to pause current song')
async def pause(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)
    if music_controller.is_playing():
        music_controller.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    

@bot.command(name='playlist', help="Tells the bot to show the current playlist")
async def get_playlist(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)
    await ctx.send(embed= await music_controller.playlist.get_formatted_playlist())


@bot.command(name='skip', help='Tells the bot to sklip the current playlist', aliases=['fs'])
async def skip(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)
    if music_controller.is_playing():
        await music_controller.skip_song()
        await ctx.send("Skipped Song :track_next:")
    else:
        await ctx.send("No song is playing to skip")


@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)
    if music_controller.is_paused():
        music_controller.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play command")
    

@bot.command(name='leave', help='Tells the bot to leave its voice channel')
async def leave(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)
    if music_controller.is_connected():
        await music_controller.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='stop', help='Tells the bot to stop the current song')
async def stop(ctx):
    music_controller = MusicController.get_music_controller(ctx.message.guild)
    if music_controller.is_playing():
        await music_controller.stop_playlist()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.command(name='volume', help='Tells the bot to set its volume')
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
        else:
            new_volume = int(args[0])
            if new_volume >= 0 and new_volume <= 100:
                new_volume = float(args[0]) / 100.0
                music_controller.set_volume(new_volume)
                await ctx.send("Set the bot's volume to :sound: {}%".format(music_controller.get_volume()))
            else:
                await ctx.send("Please enter a value between [0,100]")
    except Exception as e:
        await ctx.send("Failed to set / get bot volume")
        print(e)

@bot.event
async def on_ready():
    print("Music Bot has started.")
    for guild in bot.guilds:
        await MusicController.register_guild(guild)

@bot.event
async def on_guild_join(guild):
    print("New Guild joined.")
    await MusicController.register_guild(guild)


if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)