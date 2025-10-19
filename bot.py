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
from pyrogram.errors import FloodWait

message_queue = asyncio.Queue()

async def queue_processor(client):
    while True:
        try:
            # Wait for the first message in a new batch
            first_message, to_channel = await message_queue.get()

            # This is the start of a new batch, so wait 6 seconds to collect more messages
            await asyncio.sleep(6)

            # Create a list to hold all messages in the current batch
            batch = [(first_message, to_channel)]

            # Add any other messages that have been queued up during the delay
            while not message_queue.empty():
                batch.append(message_queue.get_nowait())

            # Process the entire batch in order
            for message, dest in batch:
                while True:
                    try:
                        await message.copy(int(dest))
                        print("Forwarded a message to", dest)
                        break  # Move to the next message
                    except FloodWait as e:
                        print(f"FloodWait: waiting for {e.value} seconds before retrying.")
                        await asyncio.sleep(e.value * 1.2)
                    except Exception as e:
                        logging.error(f"Failed to forward message: {e}")
                        break # Skip to the next message on other errors

        except asyncio.CancelledError:
            logging.info("Queue processor task cancelled.")
            break
        except Exception as e:
            logging.exception(f"An error occurred in the queue processor: {e}")


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
