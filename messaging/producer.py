from aiokafka import AIOKafkaProducer
import asyncio

class Producer:

    def __init__(self, bot):
        self._producer = None
        self.loop = bot.loop

    @classmethod
    async def create_producer(cls, bot):
        producer = Producer(bot)
        await producer.init_producer()
        return producer
    
    async def init_producer(self):
         self._producer = AIOKafkaProducer(loop=self.loop, bootstrap_servers='localhost:9092')
         await self._producer.start()

    async def send(self, topic, message):
        try:
            await self._producer.send_and_wait(topic, bytes(message, 'utf-8'))
            
        except Exception as e:
            print(f"Error: {e}")
            await self.stop()

    async def stop(self):
        await self._producer.stop()