import yt_dlp as yt_dl
import re
import spotipy
import os
from dotenv import load_dotenv


SPOTIFY_PLAYLIST_REGEX = re.compile(r'https://open.spotify.com/playlist/(\w*)')
SPOTIFY_TRACK_REGEX = re.compile(r'https://open.spotify.com/track/(\w*)')
SPOTIFY_ALBUM_REGEX = re.compile(r'https://open.spotify.com/album/(\w*)')

class Spotify:
    UNKNOWN = "UNKNOWN"
    PLAYLIST = "PLAYLIST"
    TRACK = "TRACK"
    ALBUM = "ALBUM"

load_dotenv()

YT_DL_OPTIONS = {
    'format': 'bestaudio/best',
    'restrictfilenames': False,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

spotify_client = None

try:
    spotify_client_id = os.getenv("spotify_client_id")
    spotify_client_secret = os.getenv("spotify_client_secret")
    spotify_client = spotipy.Spotify(auth_manager=spotipy.oauth2.SpotifyClientCredentials(spotify_client_id, client_secret=spotify_client_secret))
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
    
def format_duration(duration):
    mins = duration // 60
    seconds =  str(int(duration) % 60)

    if len(seconds) < 2:
        seconds = "0" + seconds

    return "{}:{}".format(mins, seconds)