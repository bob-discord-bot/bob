import asyncio
import discord
import logging
from .client import BobClient
from . import config
from .db import Guild

logging.basicConfig(level=logging.DEBUG)
intents = discord.Intents.default()
intents.message_content = True
bot = BobClient(intents=intents)


@bot.event
async def on_ready():
    logging.info("Ready!")


@bot.event
async def on_message(message: discord.Message):
    if message.author.bot or message.is_system() or message.guild is None:
        return

    guild = await Guild.get_or_none(guildId=message.guild.id)
    if guild is not None:
        if message.channel.id != guild.channelId:
            await bot.process_commands(message)
    else:
        await bot.process_commands(message)


try:
    bot.run(config.get("token"))
except KeyboardInterrupt:
    asyncio.get_running_loop().call_soon(bot.close())
