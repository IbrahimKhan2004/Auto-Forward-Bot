import logging
logger = logging.getLogger(__name__)

import asyncio
from pyrogram import filters
from bot import channelforward
from config import Config

lock = asyncio.Lock()

@channelforward.on_message(filters.channel)
async def forward(client, message):
    # Forwarding only video and sticker messages to the channel
    try:
        for id in Config.CHANNEL:
            from_channel, to_channel = id.split(":")
            if message.chat.id == int(from_channel):
                if message.video or message.sticker:
                    await asyncio.sleep(6)
                    async with lock:
                        await asyncio.sleep(6)
                        await message.copy(int(to_channel))
                        print("Forwarded a video or sticker from", from_channel, "to", to_channel)
                    await asyncio.sleep(3)
                # Removed the else block: other message types will no longer be forwarded
        await asyncio.sleep(10)
        await asyncio.sleep(15)
    except Exception as e:
        logger.exception(e)
