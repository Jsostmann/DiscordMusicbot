from collections import deque
import discord
import utils

class Playlist:
  
    def __init__(self, guild):
        self.playlist = deque()
        self.history = deque()
        self.guild = guild
        self.loop = False

    def add(self, song):        
        self.playlist.append(song)
    
    def next(self):
        if self.is_empty():
            return None
        
        if not self.loop:
            self.history.append(self.playlist.popleft())
        
        if self.is_empty():
            return None

        return self.playlist[0]

    def prev(self):
        if len(self.history) != 0:
            self.playlist.append(self.history.popleft())
    
    def is_empty(self):
        return len(self.playlist) == 0
    
    def skip(self):
        prev = self.next()
        self.history.append(prev)

    def clear(self):
        self.playlist.clear()
        self.history.clear()

    def get_size(self):
        return len(self.playlist)

    def get_playlist_duration(self):
        duration = 0
        for song in self.playlist:
            duration += song.get_value("duration")
        return utils.format_duration(duration)
    
    def get_footer(self):
        return "**{} songs in playlist | {} total length**".format(len(self.playlist), self.get_playlist_duration())
    
    def get_playlist_description(self):

        if len(self.playlist) == 0:
            return None

        description_str = ""
        for i in range(0, len(self.playlist)):
            song_content = self.playlist[i].get_embed(type="playlist")
            song_str = "`{}.` [{}]({}) | `{} requested by: {}`\n\n".format(str(i), song_content[0], song_content[1], utils.format_duration(song_content[2]), song_content[3])
            description_str += song_str

        description_str += "\n\n" + self.get_footer()
        return description_str

    async def get_formatted_playlist(self):
        description = self.get_playlist_description()

        if not description:
            return discord.Embed(title=str(self.guild) + " playlist", description="No songs in the Playlist", color=discord.Color.blue())

        embed = discord.Embed(title=str(self.guild) + " playlist", description=description, color=discord.Color.blue())
        return embed
    

