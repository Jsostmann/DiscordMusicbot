import discord
from playlist import Playlist
import utils

class MusicController:
    
    GUILD_MUSIC_CONTROLERS = {}

    @classmethod
    def get_music_controller(cls, guild_id):
        return cls.GUILD_MUSIC_CONTROLERS[guild_id]

    @classmethod
    async def register_guild(cls, guild_id):
        cls.GUILD_MUSIC_CONTROLERS[guild_id] = MusicController(guild_id)


    def __init__(self, guild):
        self.playlist = Playlist(guild)
        self.guild = guild
        self.current_song = None

    def next_song_cb(self, error):
        if not self.is_connected():
            return

        if self.playlist.is_empty():
            return
        
        else:
            n = self.playlist.next()
            print(n.get_value("channel"))
            self.process_song(n)

    def process_song(self, song):
        #play song requested if no song is being played and the queue is empty
        if not self.is_playing() and self.playlist.is_empty():
            self.current_song = song
            self.guild.voice_client.play(discord.FFmpegPCMAudio(self.current_song.get_value('url'), before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after=self.next_song_cb)
            self.guild.voice_client.source = discord.PCMVolumeTransformer(self.guild.voice_client.source)
        
        #play next song in the queue and add requested song to the queue
        elif not self.is_playing():
            self.current_song = self.playlist.next()
            self.playlist.add(song)
            self.guild.voice_client.play(discord.FFmpegPCMAudio(self.current_song.get_value('url'), before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after=self.next_song_cb)
            self.guild.voice_client.source = discord.PCMVolumeTransformer(self.guild.voice_client.source)

        #just add requested song to the back of the queue
        else:
            self.playlist.add(song)

    async def stop_playlist(self):
        self.playlist.clear()
        self.stop()
        
    async def skip_song(self):
        self.stop()

    async def disconnect(self):
        return await self.guild.voice_client.disconnect()
    
    async def connect(self, dest_channel):
        for channel in self.guild.voice_channels:
            if channel.name == dest_channel:
                await channel.connect()
                return
            
        if len(self.guild.voice_channels) > 0:
            await self.guild.voice_channels[0].connect()
            return
    
    def is_connected(self):
        return self.guild.voice_client and self.guild.voice_client.is_connected()
    
    def is_playing(self):
        return self.is_connected() and self.guild.voice_client.is_playing()
    
    def get_volume(self):
        return int(self.guild.voice_client.source.volume * 100)
    
    def set_volume(self, new_volume):
        self.guild.voice_client.source.volume = new_volume

    def pause(self):
        self.guild.voice_client.pause()

    def resume(self):
        self.guild.voice_client.resume()
    
    def is_paused(self):
        return self.is_connected() and self.guild.voice_client.is_paused()

    def is_stopped(self):
        return self.is_connected() and not self.guild.voice_client.is_playing()
    
    def stop(self):
        self.guild.voice_client.stop()
