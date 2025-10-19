import logging
logger = logging.getLogger(__name__)

from pyrogram import filters
from bot import channelforward, message_queue
from config import Config

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
