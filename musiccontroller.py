import discord
from playlist import Playlist
import utils
from song import Song
import asyncio
import concurrent.futures
#        #await asyncio.ensure_future(self.load(track, author))
#         await asyncio.ensure_future(self.load(self.playlist.playlist[i], self.playlist.playlist[i].get_value("requestee")))

class MusicController:
    
    GUILD_MUSIC_CONTROLERS = {}

    @classmethod
    def get_music_controller(cls, guild_id):
        return cls.GUILD_MUSIC_CONTROLERS[guild_id]

    @classmethod
    async def register_guild(cls, guild_id, bot):
        cls.GUILD_MUSIC_CONTROLERS[guild_id] = MusicController(guild_id, bot)


    def __init__(self, guild, bot):
        self.playlist = Playlist(guild)
        self.guild = guild
        self.current_song = None
        self.bot = bot

    def next_song_cb(self, error):
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
        song_url = utils.search_youtube(input)
        song_map = utils.create_youtube_song(song_url, author)
        song = Song(song_map)
        self.process_song_outer(song)

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
        if self.is_connected() and not self.is_playing() and self.current_song:        
            self.guild.voice_client.play(discord.FFmpegPCMAudio(self.current_song.get_value('url'), before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'), after=self.next_song_cb)
            self.guild.voice_client.source = discord.PCMVolumeTransformer(self.guild.voice_client.source)

    async def loop_song(self):
        self.playlist.loop = True if not self.playlist.loop else False
        
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
            new_volume = float(new_volume) / 100.0
            self.guild.voice_client.source.volume = new_volume
            return True
        
        return False

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
