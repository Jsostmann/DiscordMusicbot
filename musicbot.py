import discord
from discord.ext import commands, tasks
import os
from dotenv import load_dotenv
import utils
from musiccontroller import MusicController
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
                await ctx.send("<:spotify_emoji:1101667554365296650> The bot is not setup to use spotify")
                return
            
            await music_controller.play_spotify(input, author)
            await ctx.send("Playing spotify playlist :scroll:")

        else:
            await music_controller.play_youtube(input, author)
            await ctx.send("<:youtube_emoji:1101680952985518081> Playing youtube song")
            #await ctx.send(embed=song.get_embed(music_controller.playlist.get_size()))

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
        await ctx.send("<:pause:1102743418037346415> Paused Song")
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
        await ctx.send("Skipped Song <:skip:1102743429517156442>")
        return
    
    await ctx.send("No song is playing to skip")


@bot.command(name='resume', help='Resumes the song', aliases=['r'])
async def resume(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

    if music_controller.is_paused():
        music_controller.resume()
        await ctx.send("<:play:1102743419014615060> Resumed Song")
        embed = discord.Embed(description="<:play:1102743419014615060> Resumed Song")

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
        await ctx.send("Cant shuffle, only {} song in playlist".format(music_controller.get_playlist_size()))
        return

    await music_controller.shuffle_playlist()
    await ctx.send("Shuffled playlist :twisted_rightwards_arrows:")


@bot.command(name='leave', help='Tells the bot to leave its voice channel',aliases=['l'])
async def leave(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

    if music_controller.is_connected():
        await music_controller.disconnect()
        return
    else:
        await ctx.send("The bot is not connected to a voice channel.")


@bot.command(name='stop', help='Tells the bot to stop the current song',aliases=['st'])
async def stop(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()

    if music_controller.is_playing():
        await music_controller.stop_playlist()
        return
    
    await ctx.send("The bot is not playing anything at the moment.")

@bot.command(name='loop', help='Tells the bot to loop the current song')
async def loop(ctx):
    music_controller = GuildManager.get_manager(ctx.guild).get_music_controller()
 
    if music_controller.is_playing():
        await music_controller.loop_song()
        return
    await ctx.send("The bot is not playing anything at the moment, cannot loop")


@bot.command(name='volume', help='Tells the bot to set its volume',aliases=['v'])
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


@bot.command(name='emoji', help='Gets custom emojis',aliases=['e'])
async def emoji(ctx):
    found_emojis = ctx.guild.emojis

    for emoji in found_emojis:
        print(emoji)
        '''
        
        file = discord.File(utils.get_emoji_file("cd_spin_emoji.GIF"), filename="output.gif")
        print(file.filename)      
        embed = discord.Embed(title="TEST")
        embed.set_author(name="Resumed", icon_url="attachment://output.gif")
        await ctx.send(embed=embed, file=file)

        file = discord.File(utils.get_emoji_file("spotify_emoji.png"), filename="spotify_emoji.png")       
        embed = discord.Embed(title="TEST")
        embed.set_author(name="Added to the Playlist", icon_url="attachment://spotify_emoji.png")
        embed.set_thumbnail(url="attachment://spotify_emoji.png")
        await ctx.send(embed=embed, file=file)
        '''
            
async def create_emojis(guild: discord.Guild):
    emjoi_files = utils.get_emoji_files()

    for emoji_file in emjoi_files:
        emoji_name = emoji_file.split('.')[0]
        found_emoji = discord.utils.get(guild.emojis, name=emoji_name)
        if not found_emoji:
            emoji = open(utils.get_emoji_file(emoji_file), 'rb')
            await guild.create_custom_emoji(name=emoji_name, image=emoji.read())

@bot.event
async def on_ready():
    print("Music Bot has started.")
    await utils.create_image_assets()
    update_presence.start()
    for guild in bot.guilds:
        await GuildManager.register_guild(guild, bot)

        await create_emojis(guild)

@bot.event
async def on_guild_join(guild):
    print("New Guild joined.")
    await GuildManager.register_guild(guild, bot)

    await create_emojis(guild)

@tasks.loop(seconds=30)
async def update_presence():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Music Bot", details="-help for command help", state="playing music.."))


if __name__ == "__main__" :
    bot.run(DISCORD_TOKEN, reconnect=True)