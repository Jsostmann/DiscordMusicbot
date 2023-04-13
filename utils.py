import yt_dlp as yt_dl
import re

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
}

SONG_ATTRIBUTES = ["title", "requestee", "url", "duration", "thumbnail", "channel"]


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