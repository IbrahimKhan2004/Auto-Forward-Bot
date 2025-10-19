import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(lineno)d - %(module)s - %(levelname)s - %(message)s'
)
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

import asyncio
import uvloop
uvloop.install()
from config import Config
from pyrogram import Client 
from Plugins.forward import queue_processor


class channelforward(Client, Config):
    def __init__(self):
        super().__init__(
            name="CHANNELFORWARD",
            bot_token=self.BOT_TOKEN,
            api_id=self.API_ID,
            api_hash=self.API_HASH,
            workers=20,
            plugins={'root': 'Plugins'}
        )
        self.queue_processor_task = None

    async def start(self):
        await super().start()
        me = await self.get_me()
        self.queue_processor_task = asyncio.create_task(queue_processor(self))
        print(f"New session started for {me.first_name}({me.username})")

    async def stop(self):
        if self.queue_processor_task:
            self.queue_processor_task.cancel()
        await super().stop()
        print("Session stopped. Bye!!")


if __name__ == "__main__" :
    channelforward().run()
