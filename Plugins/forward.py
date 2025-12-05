import logging
logger = logging.getLogger(__name__)

import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait
from bot import channelforward
from config import Config

# Queue to hold (message_id, message, destination_channel_id)
# We store message_id explicitly for sorting.
message_queue = []
worker_busy = False

async def worker():
    global worker_busy
    print("Worker started")

    while message_queue:
        # Sort queue by message ID (first element of tuple)
        # This ensures that even if messages arrive out of order, they are forwarded in order.
        message_queue.sort(key=lambda x: x[0])

        msg_id, msg, dest = message_queue[0]

        try:
            print(f"Processing message {msg_id} for destination {dest}")
            if msg.reply_markup:
                await msg.copy(int(dest), reply_markup=msg.reply_markup)
            else:
                await msg.copy(int(dest))
            print(f"Forwarded message {msg_id} to {dest}")

            # Remove from queue only after successful attempt (or if we decide to skip)
            # Actually, to prevent infinite loops on error, we should probably pop first or handle exceptions carefully.
            # But the original code popped after success or generic exception, but retried on FloodWait.
            message_queue.pop(0)

            await asyncio.sleep(3)

        except FloodWait as e:
            print(f"FloodWait: sleeping for {e.value * 1.2}s")
            await asyncio.sleep(e.value * 1.2)
            # We do NOT pop the message, so we retry it.
            continue

        except Exception as e:
            logger.exception(e)
            print(f"Failed to forward message {msg_id}: {e}")
            message_queue.pop(0)
            pass

    worker_busy = False
    print("Worker finished queue")


@channelforward.on_message(filters.channel)
async def forward(client, message):
    global worker_busy
    try:
        # Check if message is from a configured source channel
        for channel_pair in Config.CHANNEL:
            from_channel, to_channel = channel_pair.split(":")

            if message.chat.id == int(from_channel):
                if message.video or message.sticker:
                    # Append to queue
                    # structure: (message_id, message_object, destination_id)
                    message_queue.append((message.id, message, to_channel))
                    print(f"Added message {message.id} to queue for {to_channel}")

                    # Start worker if not running
                    if not worker_busy:
                        worker_busy = True
                        asyncio.create_task(worker())

    except Exception as e:
        logger.exception(e)
