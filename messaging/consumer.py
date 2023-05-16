from aiokafka import AIOKafkaConsumer
import asyncio

class Consumer:

    def __init__(self, bot, topics):
        self._consumer = None
        self.loop = bot.loop
        self.topics = topics

    @classmethod
    async def create_consumer(cls, bot, topics):
        consumer = Consumer(bot, topics)
        await consumer.init_consumer()
        return consumer

    async def init_consumer(self):
         await asyncio.sleep(10)
         self._consumer =  AIOKafkaConsumer(*self.topics, loop=self.loop, bootstrap_servers='localhost:9092')
         self.loop.create_task(self.run())
        
    async def run(self):
        await self._consumer.start()

        while True:
            try:
                async for msg in self._consumer:
                    print("consumed: ", msg.topic, msg.partition, msg.offset, msg.key, msg.value, msg.timestamp)

            except Exception as e:
                print(f"Error: {e}")
                await self.stop()

    async def stop(self):
        await self._consumer.stop()