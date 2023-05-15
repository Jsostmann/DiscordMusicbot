import yt_dlp as yt_dl
import re
from spotipy import Spotify as SpotifyClient
from spotipy.oauth2 import SpotifyClientCredentials
import os
import hashlib
import httpx
import discord
from dotenv import load_dotenv

load_dotenv()

DB_SCHEMA_NAME = "schema.sql"
DB_NAME = "database.db"
DEFAULT_SETTINGS = lambda guild_id: [(guild_id, "cooldown-time", 120),(guild_id, "cooldown-freq", 4), (guild_id, "blacklist", True), (guild_id, "whitelist", True), (guild_id, "restart", False)]

DB_PATH = os.path.join(os.getcwd(), "database", DB_NAME)
DB_SCHEMA_PATH = os.path.join(os.getcwd(), "database", DB_SCHEMA_NAME)

SPOTIFY_PLAYLIST_REGEX = re.compile(r'https://open.spotify.com/playlist/(\w*)')
SPOTIFY_TRACK_REGEX = re.compile(r'https://open.spotify.com/track/(\w*)')
SPOTIFY_ALBUM_REGEX = re.compile(r'https://open.spotify.com/album/(\w*)')

DISCORD_APPLICATION_ID = os.getenv("discord_application_id")
DISCORD_URL = "https://discordapp.com/api/oauth2/applications/{}/assets"
DISCORD_ASSET_URL = "https://cdn.discordapp.com/app-assets/{}/{}.png?size={}"

class Spotify:
    UNKNOWN = "UNKNOWN"
    PLAYLIST = "PLAYLIST"
    TRACK = "TRACK"
    ALBUM = "ALBUM"

YT_DL_OPTIONS = {
    'format': 'bestaudio/best',
    'restrictfilenames': False,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto'
}

spotify_client = None
asset_map = {}
emoji_map = {}

try:
    spotify_client_id = os.getenv("spotify_client_id")
    spotify_client_secret = os.getenv("spotify_client_secret")
    spotify_client = SpotifyClient(auth_manager=SpotifyClientCredentials(spotify_client_id, client_secret=spotify_client_secret))
    spotify_enabled = True
except:
    spotify_enabled = False

def spotify_enabled():
    return spotify_enabled

def is_spotify_input(input):
    if not "spotify.com" in input:
        return Spotify.UNKNOWN
    
    if Spotify.TRACK.lower() in input:
        return Spotify.TRACK

    if Spotify.ALBUM.lower() in input:
        return Spotify.ALBUM

    if Spotify.PLAYLIST.lower() in input:
        return Spotify.PLAYLIST
    
    return Spotify.UNKNOWN

def get_spotify_album(input):
    album_id = get_spotify_media_id(input, SPOTIFY_ALBUM_REGEX)

    if not album_id:
        return None
    
    album = spotify_client.album_tracks(album_id=album_id)

    return ["{}, {}".format(track['name'], track['artists'][0]['name']) for track in album['items']]
    
def get_spotify_track(input):
    track_id = get_spotify_media_id(input, SPOTIFY_TRACK_REGEX)

    if not track_id:
        return None
    
    track = spotify_client.track(track_id=track_id)

    return ["{}, {}".format(track['name'], track['artists'][0]['name'])]
    
def get_spotify_playlist(input):
    playlist_id = get_spotify_media_id(input, SPOTIFY_PLAYLIST_REGEX)

    if not playlist_id:
        return None
    
    tracks = spotify_client.playlist_tracks(playlist_id=playlist_id, fields="items(track(name, artists(name)))")

    if not tracks:
        return False
    
    tracks = tracks["items"]

    return ["{}, {}".format(track['track']['name'], track['track']['artists'][0]['name']) for track in tracks]

def get_spotify_media_id(input, media_regex):
    media_id = media_regex.search(input)

    if not media_id:
        return None
    
    return media_id.group(0)

def get_spotify_input(input, spotify_type):
    match spotify_type:
        case Spotify.TRACK:
            return get_spotify_track(input)
        case Spotify.ALBUM:
            return get_spotify_album(input)
        case Spotify.PLAYLIST:
            return get_spotify_playlist(input)
    
def search_youtube(title):
    
    # If URL is provided return
    if get_url(title) is not None:
        return title

    # if song name is provided, search and return song URL
    with yt_dl.YoutubeDL(YT_DL_OPTIONS) as ydl:
        result = ydl.extract_info(title, download=False)

        if not result:
            return None

        video_id = result['entries'][0]['id']

        return "https://www.youtube.com/watch?v={}".format(video_id)

def create_youtube_song(url, author):
    with yt_dl.YoutubeDL(YT_DL_OPTIONS) as ydl:
        result = ydl.extract_info(url, download=False)

        if not result:
            return None
        
        result.update({"requestee": author})

        return result

def get_url(content):
    regex = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")
    if re.search(regex, content):
        result = regex.search(content)
        url = result.group(0)
        return url
    else:
        return None
    
def to_hash(data):
    sha1 = hashlib.sha1()
    sha1.update(data.encode('utf-8'))
    return sha1.hexdigest()

def format_duration(duration):
    mins = duration // 60
    hours = mins // 60
    seconds =  str(int(duration) % 60)

    add_padding = lambda t : "0" + t if len(t) < 2 else t

    seconds = add_padding(str(seconds))
    mins = add_padding(str(mins))
    hours = add_padding(str(hours))

    return f"{hours}:{mins}:{seconds}"

def format_date(date_str):
    date_str = str(date_str)
    if not len(date_str) == 8:
        return None
    return "{}-{}-{}".format(date_str[4:6], date_str[6:8], date_str[:4])

def get_image_asset(asset_name, size):
    return asset_map[asset_name][size]

async def create_image_assets():
    global asset_map
    asset_map = {}
    async with httpx.AsyncClient() as client:
        assets = await client.get(DISCORD_URL.format(DISCORD_APPLICATION_ID))
        for asset in assets.json():
            asset_map[asset['name']] = tuple(DISCORD_ASSET_URL.format(DISCORD_APPLICATION_ID, asset['id'], size) for size in [40, 128, 512])

async def create_emojis(guild: discord.guild.Guild):
    global emoji_map
    emjoi_files = get_emoji_files()

    for emoji_file in emjoi_files:
        emoji_name = emoji_file.split('.')[0]
        found_emoji = discord.utils.get(guild.emojis, name=emoji_name)

        if not found_emoji:
            emoji = open(get_emoji_file(emoji_file), 'rb')
            found_emoji = await guild.create_custom_emoji(name=emoji_name, image=emoji.read())
            
        emoji_map[emoji_name] = found_emoji

async def delete_emojis(guild: discord.guild.Guild):
    emjoi_files = get_emoji_files()

    for emoji_file in emjoi_files:
        emoji_name = emoji_file.split('.')[0]
        found_emoji = discord.utils.get(guild.emojis, name=emoji_name)
        if found_emoji:
            await guild.delete_emoji(found_emoji)

def get_emoji_files():
    return os.listdir(os.path.join(os.getcwd(), "assets", "emojis"))

def embed_local_image(embed, file_name, embed_type=["thumbnail", "image", "author"]):
    file_obj = os.path.join(os.getcwd(), "assets", "emojis", file_name)

    match embed_type:
        case "thumbnail":
            embed.set_thumbnail(url=f"attachment://{file_name}")
        case "image":
            embed.set_image(url=f"attachment://{file_name}")
        case "author":
            embed.author.icon_url = f"attachment://{file_name}"

    file = discord.File(file_obj, filename=file_name)
    return file

def get_emoji_file(emoji_file_name):
    return os.path.join(os.getcwd(), "assets", "emojis", emoji_file_name)