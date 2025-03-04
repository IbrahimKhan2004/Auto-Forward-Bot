import logging
logger = logging.getLogger(__name__)

import asyncio
from pyrogram import filters
from bot import channelforward
from config import Config 

@channelforward.on_message(filters.channel)
async def forward(client, message):
    # Forwarding the messages to the channel
    try:
        for id in Config.CHANNEL:
            from_channel, to_channel = id.split(":")
            if message.chat.id == int(from_channel):
                await asyncio.sleep(3)  # Adding delay before forwarding
                await message.copy(int(to_channel))
                print("Forwarded a message from", from_channel, "to", to_channel)
                await asyncio.sleep(10)
    except Exception as e:
        logger.exception(e)
