from __future__ import annotations

from controllers.musiccontroller import MusicController
from controllers.settingscontroller import SettingsController
import modules.utils as utils
from messaging.producer import Producer
from messaging.consumer import Consumer

class GuildManager:
    
    GUILD_MANAGERS = {}
    PRODUCER = None
    CONSUMER = None

    @classmethod
    async def create(cls, bot, *topics):
        cls.PRODUCER = await Producer.create_producer(bot)
        cls.CONSUMER = await Consumer.create_consumer(bot, topics)

    @classmethod
    def get_manager(cls, guild) -> GuildManager:
        return cls.GUILD_MANAGERS[guild.id]

    @classmethod
    async def register_guild(cls, guild, bot)-> None:
        cls.GUILD_MANAGERS[guild.id] = await cls.create_new_guild_manager(guild, bot)
        await utils.create_image_assets()
        await utils.create_emojis(guild)

    @classmethod
    async def create_new_guild_manager(cls, guild, bot):
        manager = GuildManager(guild, bot)
        manager.settings_controller = await SettingsController.create_settings_controller(guild, bot)
        return manager
    
    def __init__(self, guild, bot):
        self.bot = bot
        self.music_controller = MusicController(guild, bot)
        self.settings_controller = None

    def get_music_controller(self) -> MusicController:
        return self.music_controller

    def get_settings_controller(self) -> SettingsController:
        return self.settings_controller