import logging
logger = logging.getLogger(__name__)

import asyncio
from pyrogram import filters
from bot import channelforward
from config import Config

message_queue = asyncio.Queue()

async def queue_processor(client):
    while True:
        try:
            # Wait for the first message
            message, to_channel = await message_queue.get()

            # After receiving the first message, wait 6 seconds to collect other messages
            await asyncio.sleep(3)

            # Process the first message
            try:
                await message.copy(int(to_channel))
                print("Forwarded a message to", to_channel)
            except Exception as e:
                logger.error(f"Failed to forward message: {e}")

            # Process any other messages that have been queued up
            while not message_queue.empty():
                message, to_channel = await message_queue.get()
                try:
                    await message.copy(int(to_channel))
                    print("Forwarded a message to", to_channel)
                except Exception as e:
                    logger.error(f"Failed to forward message: {e}")

        except asyncio.CancelledError:
            logger.info("Queue processor task cancelled.")
            break
        except Exception as e:
            logger.exception(f"An error occurred in the queue processor: {e}")

@channelforward.on_message(filters.channel)
async def forward(client, message):
    try:
        for id in Config.CHANNEL:
            from_channel, to_channel = id.split(":")
            if message.chat.id == int(from_channel):
                if message.video or message.sticker:
                    await message_queue.put((message, to_channel))
                    print("Added a message to the queue from", from_channel)
    except Exception as e:
        logger.exception(e)
