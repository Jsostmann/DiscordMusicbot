import asyncio
import modules.utils as utils
import time

class AsyncSongtimer:
    def __init__(self, bot):
        self.song_timer = None
        self.song_time = 0
        self.bot = bot

    async def song_task(self):
        while True:
            self.song_time += 1
            await asyncio.sleep(1)

    def get_time(self):
        return utils.format_duration(self.song_time)
    
    def pause(self):
        if self.song_time:
            self.song_timer.cancel()
            self.song_timer = None

    def resume(self):
        self.start()

    def stop(self):
        if self.song_time:
            self.song_timer.cancel()
            self.song_timer = None
            self.song_time = 0

    def start(self):
        if not self.song_timer:
            self.song_timer = self.bot.loop.create_task(self.song_task())

class Songtimer:
    def __init__(self):
        self.song_time = 1
        self.last_check = time.time()
        self.paused = False

    def update_time(self):
        current = time.time()
        self.song_time += int(current - self.last_check)
        self.last_check = current

    def get_time(self):
        if not self.paused:
            self.update_time()
        
        return utils.format_duration(self.song_time)
    
    def pause(self):
        self.paused = True

    def resume(self):
        self.last_check = time.time()
        self.paused = False

    def stop(self):
        self.song_time = 1
        self.last_check = time.time()
        self.paused = False

    def start(self):
        self.song_time = 1
        self.last_check = time.time()
        self.paused = False