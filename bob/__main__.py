import asyncio
import discord
import logging
from .client import BobClient
from . import config

logging.basicConfig(level=logging.DEBUG)
intents = discord.Intents.default()
intents.message_content = True
bot = BobClient(intents=intents)


@bot.event
async def on_ready():
    logging.info("Ready!")


try:
    bot.run(config.get("token"))
except KeyboardInterrupt:
    asyncio.get_running_loop().call_soon(bot.close())
