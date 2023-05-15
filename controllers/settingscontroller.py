import discord
from models.playlist import Playlist
import modules.utils as utils
from models.song import Song
import time
from modules import database as db

class SettingsController:
        
    def __init__(self, guild, bot):
        self.bot = bot
        self.guild = guild
        self.whitelist = list([guild.owner.id])
        self.blacklist = list()
        self.cooldown_map = dict()
        self.cooldown_frequency = 3
        self.cooldown_time_seconds = 120
        self.settings = None

    @classmethod
    async def create_settings_controller(cls, guild, bot):
        controller = SettingsController(guild, bot)
        await controller.init_settings()
        return controller

    async def init_settings(self):
        self.settings = await db.get_guild_settings(self.guild.id)

    def user_has_cooldown(self, user_id: int) -> bool:
        if user_id in self.whitelist or user_id:
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
    
    def get_remaining_cooldown(self, user_id: int) -> str:
        if not user_id in self.cooldown_map:
            return None

        cooldown_endtime = self.cooldown_map[user_id][0] + self.cooldown_time_seconds
        return utils.format_duration(int(cooldown_endtime - time.time()))
    

    async def blacklist_user(self, guild_id: int, user_id: int) -> int:
        if user_id in self.settings["blacklist"]:
            return 2
        
        if user_id in self.settings["whitelist"]:
            self.settings["whitelist"].remove(user_id)
            #todo remove DB record of whitelisted user

        success = await db.insert_listed_user("blacklist", guild_id, user_id)
        if not success:
            return 0
        
        self.settings["blacklist"].append(user_id)
        return 1
    

    async def whitelist_user(self, guild_id: int, user_id: int) -> int:
        if user_id in self.settings["whitelist"]:
            return 2
        
        if user_id in self.settings["blacklist"]:
            self.settings["blacklist"].remove(user_id)
            #todo remove DB record of blacklisted user

        success = await db.insert_listed_user("blacklist", guild_id, user_id)
        if not success:
            return 0
        
        self.settings["blacklist"].append(user_id)
        return 1
    

    def is_user_blacklisted(self, user_id: int) -> bool:
        return user_id in self.settings["blacklist"]
    