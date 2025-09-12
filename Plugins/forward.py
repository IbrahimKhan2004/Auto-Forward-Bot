import logging
logger = logging.getLogger(__name__)

import asyncio
from pyrogram import filters
from bot import channelforward
from config import Config

# Using an asyncio.Queue to ensure messages are processed in order
message_queue = asyncio.Queue()
lock = asyncio.Lock()

async def process_messages_from_queue():
    while True:
        message = await message_queue.get()
        try:
            for id in Config.CHANNEL:
                from_channel, to_channel = id.split(":")
                if message.chat.id == int(from_channel):
                    if message.video or message.sticker:
                        await asyncio.sleep(3) # Delay after receiving
                        async with lock:
                            await message.copy(int(to_channel))
                            print("Forwarded a video or sticker from", from_channel, "to", to_channel)
                        await asyncio.sleep(3) # Delay after forwarding
        except Exception as e:
            logger.exception(e)
        finally:
            message_queue.task_done()

@channelforward.on_message(filters.channel)
async def forward(client, message):
    # Only enqueue video and sticker messages from the source channel
    for id in Config.CHANNEL:
        from_channel, to_channel = id.split(":")
        if message.chat.id == int(from_channel):
            if message.video or message.sticker:
                await message_queue.put(message)
                break # Assuming a message only needs to be processed for one channel pair

# Start the message processing task when the bot starts
@channelforward.on_ready
async def start_queue_processor(client):
    asyncio.create_task(process_messages_from_queue())
