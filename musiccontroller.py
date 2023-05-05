import discord
from playlist import Playlist
import utils
from song import Song
import asyncio
import concurrent.futures
import random
from songtimer import Songtimer

class MusicController:
    
    def __init__(self, guild, bot):
        self.bot = bot
        self.playlist = Playlist(guild)
        self.song_timer = Songtimer()
        self.guild = guild
        self.current_song = None
        self.volume = 100

    def next_song_cb(self, error) -> None:

        self.song_timer.stop()

        if not self.is_connected():
            return
        
        self.current_song = self.playlist.next()

        if not self.current_song:
            return
        
        self.process_song()

    async def play_spotify(self, input, author):
        media_type = utils.is_spotify_input(input)

        if media_type == utils.Spotify.UNKNOWN:
            return None
        
        track_names = utils.get_spotify_input(input, media_type)
        
        for track in track_names:
            song_url = await self.bot.loop.run_in_executor(None, utils.search_youtube, track)
            song_map = await self.bot.loop.run_in_executor(None, utils.create_youtube_song, song_url, author)
            song = Song(song_map)
            self.process_song_outer(song)

    async def play_youtube(self, input, author):
        song_url = await self.bot.loop.run_in_executor(None, utils.search_youtube, input)
        song_map = await self.bot.loop.run_in_executor(None, utils.create_youtube_song, song_url, author)
        song = Song(song_map)
        self.process_song_outer(song)
        return song

    async def load(self, song: Song, author):

        if song.is_loaded():
            return
        
        def download(song):
            youtube_url = utils.search_youtube(song.get_value("title"))
            youtube_song = utils.create_youtube_song(youtube_url, author)
            song.set_song_map(youtube_song)
            song.set_loaded(True)

        loop = asyncio.get_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        fin, pen = await asyncio.wait(fs={loop.run_in_executor(executor, download, song)}, return_when=asyncio.FIRST_COMPLETED)

    def process_song_outer(self, song):
        self.playlist.add(song)

        if not self.current_song:
            self.current_song = song

        self.process_song()

    def process_song(self):
        #play song requested if no song is being played and the queue is empty
        #TODO check if song is paused before trying to play anything

        if self.is_connected() and not (self.is_playing() or self.is_paused()) and self.current_song:        
            self.guild.voice_client.play(discord.FFmpegPCMAudio(self.current_song.get_value('url'), before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after=self.next_song_cb)
            self.guild.voice_client.source = discord.PCMVolumeTransformer(self.guild.voice_client.source, self.volume / 100.0)
            self.song_timer.start()

    async def get_current_song(self):
        play_time = self.song_timer.get_time()
        return self.current_song.get_embed(0, play_time, "detailed")

    def playlist_is_empty(self):
        return self.playlist.is_empty()

    def get_playlist_size(self):
        return self.playlist.get_size()
    
    async def shuffle_playlist(self):
        for i in range(1, self.playlist.get_size()):
            swap_index = random.randrange(1, self.playlist.get_size())
            self.playlist.playlist[i], self.playlist.playlist[swap_index] = self.playlist.playlist[swap_index], self.playlist.playlist[i]

    async def loop_song(self):
        if self.is_playlist_looping():
           self.playlist.loop_playlist = False 

        self.playlist.loop_song = True if not self.playlist.loop_song else False

    async def loop_playlist(self):
        if self.is_song_looping():
           self.playlist.loop_song = False 

        self.playlist.loop_playlist = True if not self.playlist.loop_playlist else False

    def is_song_looping(self):
        return self.playlist.loop_song

    def is_playlist_looping(self):
        return self.playlist.loop_playlist
    
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
        if new_volume >= 0 and new_volume <= 100:
            self.volume = float(new_volume) / 100.0
            self.guild.voice_client.source.volume = self.volume
            return True
        
        return False

    def pause(self):
        self.guild.voice_client.pause()
        self.song_timer.pause()

    def resume(self):
        if self.is_paused():
            self.guild.voice_client.resume()
            self.song_timer.resume()
            return
        
        self.process_song()
    
    def can_resume(self):
        return self.is_paused() or (self.is_stopped() and not self.playlist_is_empty())

    def is_paused(self):
        return self.is_connected() and self.guild.voice_client.is_paused()

    def is_stopped(self):
        return self.is_connected() and not self.guild.voice_client.is_playing()
    
    def stop(self):
        self.guild.voice_client.stop()
