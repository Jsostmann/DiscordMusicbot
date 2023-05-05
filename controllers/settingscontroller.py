import sys
sys.dont_write_bytecode = True

import discord
from models.playlist import Playlist
import utils
from models.song import Song
import time

class SettingsController:
        
    def __init__(self, guild, bot):
        self.bot = bot
        self.guild = guild
        self.cooldown_whitelist = list()
        self.black_list = list()
        self.cooldown_map = dict()
        self.cooldown_frequency = 3
        self.cooldown_time_seconds = 120

    def user_has_cooldown(self, user_id: int) -> bool:
        if user_id in self.cooldown_whitelist:
            return False
        
        if not user_id in self.cooldown_map:
            self.cooldown_map[user_id] = (time.time(), 1)
            return False
        
        user_time, user_freq = self.cooldown_map[user_id]

        if (time.time() - user_time) > self.cooldown_time_seconds:
            self.cooldown_map[user_id] = (time.time(), 1)
            return False
        
        if user_freq < self.cooldown_frequency:
            self.cooldown_map[user_id] = (user_time, user_freq + 1)
            return False
        
        return True
    
    def is_user_blacklisted(self, user_id: int) -> bool:
        return user_id in self.black_list
    