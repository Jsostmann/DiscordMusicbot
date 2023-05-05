from __future__ import annotations
from musiccontroller import MusicController
from settingscontroller import SettingsController
import utils

class GuildManager:
    
    GUILD_MANAGERS = {}

    @classmethod
    def get_manager(cls, guild_id) -> GuildManager:
        return cls.GUILD_MANAGERS[guild_id]

    @classmethod
    async def register_guild(cls, guild_id, bot)-> None:
        cls.GUILD_MANAGERS[guild_id] = GuildManager(guild_id, bot)
        await utils.create_image_assets()
        await utils.create_emojis(guild_id)

    def __init__(self, guild, bot):
        self.bot = bot
        self.music_controller = MusicController(guild, bot)
        self.settings_controller = SettingsController(guild, bot)
    
    def get_music_controller(self) -> MusicController:
        return self.music_controller

    def get_settings_controller(self) -> SettingsController:
        return self.settings_controller