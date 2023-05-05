from collections import deque
import discord
import utils

class Playlist:
  
    def __init__(self, guild):
        self.playlist = deque()
        self.history = deque()
        self.guild = guild
        self.loop_song = False
        self.loop_playlist = False

    def add(self, song):        
        self.playlist.append(song)
    
    def next(self):
        if self.is_empty():
            return None
        
        if self.loop_playlist:
            self.add(self.playlist.popleft())

        if not (self.loop_song or self.loop_playlist):
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
        pluarl_song = ''
        
        if len(self.playlist) > 1:
            pluarl_song = 's'

        check_loop = lambda loop : ":white_check_mark:" if loop else ":x:"
        loop_str = f"Loop song: {check_loop(self.loop_song)} | Loop playlist {check_loop(self.loop_playlist)}"
        return f"**{len(self.playlist)} song{pluarl_song} in playlist | {self.get_playlist_duration()} total length** \n {loop_str}"
    
    def get_playlist_description(self):

        if len(self.playlist) == 0:
            return None

        description_str = ""
        for i in range(0, len(self.playlist)):
            song_content = self.playlist[i].get_embed(type="playlist")

            if i == 0:
                description_str += f"__Now Playing__:\n[{song_content[0]}]({song_content[1]}) | `{utils.format_duration(song_content[2])} requested by: {song_content[3]}`\n\n"
                continue
            if i == 1:
                description_str += f"__Up Next__:\n`{str(i)}.` [{song_content[0]}]({song_content[1]}) | `{utils.format_duration(song_content[2])} requested by: {song_content[3]}`\n\n"
                continue

            description_str += f"`{str(i)}.` [{song_content[0]}]({song_content[1]}) | `{utils.format_duration(song_content[2])} requested by: {song_content[3]}`\n\n"

        description_str += "\n" + self.get_footer()
        return description_str

    async def get_formatted_playlist(self):
        description = self.get_playlist_description()

        if not description:
            return discord.Embed(title=str(self.guild) + " playlist", description="No songs in the Playlist", color=discord.Color.blue())

        embed = discord.Embed(title=str(self.guild) + " playlist", description=description, color=discord.Color.blue())
        return embed
    

