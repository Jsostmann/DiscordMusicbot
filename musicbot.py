import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import yt_dlp as yt_dl
from playlist import Playlist
from song import Song
import utils

load_dotenv()
DISCORD_TOKEN = os.getenv("discord_token")

intents = discord.Intents().all()
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='-', intents=intents)


playlist = Playlist()
current_song = None
GUILD_MAP = {}
GUILD = None

def next_song_cb(error):
    global current_song
    current_song = None
    print("CB")
    if playlist.is_empty():
        return
    else:
        n = playlist.next()
        print(n.get_value("channel"))
        process_song(n)

def process_song(song):
    global current_song
    print(current_song)
    if not current_song:
        current_song = song
        GUILD.voice_client.play(discord.FFmpegPCMAudio(current_song.get_value('url'), before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after=lambda e: next_song_cb(e))
        GUILD.voice_client.source = discord.PCMVolumeTransformer(GUILD.voice_client.source)
    else:
        playlist.add(song)

@bot.command(name='play', help='Play a song')
async def play(ctx, *, url):
    global GUILD
    try :
        current_server = ctx.message.guild
        GUILD = current_server
        voice_channel = current_server.voice_client
        author = ctx.message.author

        if not voice_channel or not voice_channel.is_connected():
            await ctx.send("The bot is not connected to a voice channel.")
            return

        if not author.voice:
            await ctx.send("Cannot play song {} is not currently in a voice channel".format(author.name))
            return
        
        song_url = utils.search_youtube(url)
        downloader = yt_dl.YoutubeDL(utils.YT_DL_OPTIONS)
        
        result_map = downloader.extract_info(song_url, download=False)
        result_map.update({"requestee": author})

        song = Song(result_map)

        async with ctx.typing():
            process_song(song)
            await ctx.send(embed=song.get_embed(playlist.get_size() + 1))

    except Exception as e:
        await ctx.send("Error playing song")
        print(e.with_traceback())


@bot.command(name='join', help='Tells the bot to join the senders voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
    else:
        channel = ctx.message.author.voice.channel
        await channel.connect()


@bot.command(name='pause', help='Tells the bot to pause current song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")
    

@bot.command(name='playlist', help="Tells the bot to show the current playlist")
async def get_playlist(ctx):
    if playlist.is_empty():
        await ctx.send("No songs currently in the playlist")
    else:
        await ctx.send(embed= await playlist.get_formatted_playlist())


@bot.command(name='skip', help='Resumes the song')
async def skip(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play command")


@bot.command(name='resume', help='Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")
    

@bot.command(name='leave', help='Tells the bot to leave its voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='stop', help='Tells the bot to stop the current song')
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")


@bot.command(name='volume', help='Tells the bot to set its volume')
async def volume(ctx, *args):
    voice_client = ctx.message.guild.voice_client

    if voice_client and voice_client.is_connected() and voice_client.is_playing():
        try:  
            if len(args) == 0:          
                await ctx.send("Bots current volume :speaker: {}".format(voice_client.source.volume))
            else:
                voice_client.source.volume = float(args[0]) / 100.0
                await ctx.send("Set the bot's volume to :sound: {}".format(voice_client.source.volume))

        except Exception as e:
            await ctx.send("Failed to set / get bot volume")
            print(e)
    else:
        await ctx.send("The bot is not in a voice channel")




@bot.event
async def on_ready():
    global GUILD
    print('Running!')
    for guild in bot.guilds:
        GUILD_MAP[guild] = bot
        GUILD = guild
        for channel in guild.text_channels :
            if str(channel) == "general" :
                await channel.send('Bot Activated..')
        print('Active in {}\n Member Count : {}'.format(guild.name,guild.member_count))


@bot.command(help = "Prints details of Server")
async def where_am_i(ctx):
    owner=str(ctx.guild.owner)
    guild_id = str(ctx.guild.id)
    memberCount = str(ctx.guild.member_count)
    desc=ctx.guild.description

    embed = discord.Embed(
        title=ctx.guild.name + " Server Information",
        description=desc,
        color=discord.Color.blue()
    )
    embed.add_field(name="Owner", value=owner, inline=True)
    embed.add_field(name="Server ID", value=guild_id, inline=True)
    embed.add_field(name="Member Count", value=memberCount, inline=True)

    await ctx.send(embed=embed)

    members=[]
    async for member in ctx.guild.fetch_members(limit=150) :
        await ctx.send('Name : {}\t Status : {}\n Joined at {}'.format(member.display_name,str(member.status),str(member.joined_at)))

@bot.event
async def on_member_join(member):
     for channel in member.guild.text_channels :
         if str(channel) == "general" :
             on_mobile=False
             if member.is_on_mobile() == True :
                 on_mobile = True
             await channel.send("Welcome to the Server {}!!\n On Mobile : {}".format(member.name,on_mobile))



if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN)