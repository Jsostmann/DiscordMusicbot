import discord
from playlist import Playlist
import utils

class MusicController:
  
    def __init__(self, guild):
        self.playlist = Playlist()

    def add(self, song):        
        self.playlist.append(song)
    



    

