import logging
logger = logging.getLogger(__name__)

import asyncio
from pyrogram import filters
from bot import channelforward
from config import Config

lock = asyncio.Lock()
message_queue = []

@channelforward.on_message(filters.channel)
async def forward(client, message):
    try:
        for id in Config.CHANNEL:
            from_channel, to_channel = id.split(":")
            if message.chat.id == int(from_channel):
                if message.video or message.sticker:
                    async with lock:
                        message_queue.append((message, to_channel))
                        if len(message_queue) == 1:
                            while message_queue:
                                msg, dest = message_queue[0]
                                await msg.copy(int(dest))
                                print("Forwarded in order from", from_channel, "to", dest)
                                message_queue.pop(0)
                                await asyncio.sleep(2)
    except Exception as e:
        logger.exception(e)
