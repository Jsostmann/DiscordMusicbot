import utils
import discord

class Song:

    SONG_ATTRIBUTES = ["title", "requestee", "url", "webpage_url", "duration", "thumbnail", "channel" ,"like_count", "view_count", "upload_date"]

    def __init__(self, raw_map):
        if raw_map:
            self.song_map = Song.parse_song(raw_map)
        else:
            self.song_map = {}

    def set_value(self, key: any, value: any) -> None:
        if key in Song.SONG_ATTRIBUTES:
            self.song_map[key] = value

    def set_song_map(self, song_map: dict) -> None:
        self.song_map = Song.parse_song(song_map)

    def get_value(self, value) -> any:
        if value in self.song_map:
            return self.song_map[value]
    #todo
    def get_embed_new(self, pos, current_time=None, type=["playlist", "song"]):
        if type == "playlist":
            return self.get_playlist_format()
        

        author = self.get_value("requestee").avatar
        duration = utils.format_duration(self.get_value("duration"))
        song_title = self.get_value("title")
        thumbnail = self.get_value("thumbnail")
        song_url = self.get_value("webpage_url")
        channel = self.get_value("channel")


        embed = discord.Embed(title=song_title, url=song_url)
        embed.set_author(name="Added to the Playlist", icon_url=author)
        embed.set_thumbnail(url=thumbnail)

        embed.add_field(name="Channel", value=channel, inline=True)
        embed.add_field(name="Duration", value=duration, inline=True)

        if current_time:
            embed.add_field(name="Current Time", value=current_time, inline=True)

        embed.add_field(name="Position in Playlist", value=pos, inline=False)

        return embed
    
    def get_embed(self, pos, current_time=None):
        author = self.get_value("requestee").avatar
        duration = utils.format_duration(self.get_value("duration"))
        song_title = self.get_value("title")
        thumbnail = self.get_value("thumbnail")
        song_url = self.get_value("webpage_url")
        channel = self.get_value("channel")


        embed = discord.Embed(title=song_title, url=song_url)
        embed.set_author(name="Added to the Playlist", icon_url=author)
        embed.set_thumbnail(url=thumbnail)

        embed.add_field(name="Channel", value=channel, inline=True)
        embed.add_field(name="Duration", value=duration, inline=True)
        if current_time:
            embed.add_field(name="Current Time", value=current_time, inline=True)
        embed.add_field(name="Position in Playlist", value=pos, inline=False)

        return embed
    
    def get_playlist_format(self):
        '''
            Returns song in format to be used when showing playlist
        '''
        return (self.get_value("title"), self.get_value("duration"), self.get_value("requestee").name)

    @classmethod
    def parse_song(cls, raw_map: dict):
        attrib_map = {}
        for attrib in Song.SONG_ATTRIBUTES:
            if attrib in raw_map:
                attrib_map[attrib] = raw_map[attrib]

        return attrib_map