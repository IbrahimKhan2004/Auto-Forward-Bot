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
                # MODIFICATION START: Check if the message is a video or sticker
                if message.video or message.sticker: 
                    await asyncio.sleep(20)  # Adding delay before forwarding
                    await message.copy(int(to_channel))
                    print("Forwarded a video or sticker from", from_channel, "to", to_channel) # MODIFICATION: Updated print statement for clarity
                    await asyncio.sleep(25)
                # MODIFICATION END
                # ADDITION START
                else:
                    await asyncio.sleep(6) # Add delay for single video post
                # ADDITION END
    except Exception as e:
        logger.exception(e)
