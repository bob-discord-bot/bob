import asyncio
import discord
import logging
import argparse
from .client import BobClient
from . import config, __version__
from .db import Guild

parser = argparse.ArgumentParser(description=f"bob {__version__}")
parser.add_argument("--debug", "-d", action="store_true", help="enable debug mode")
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format="[%(asctime)s / %(levelname)s] %(name)s: %(message)s",
)

intents = discord.Intents.default()
intents.message_content = True
bot = BobClient(
    intents=intents,
    command_prefix="bc." if args.debug else "b.",
)


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
    bot.run(config.get("token"), log_handler=None)
except KeyboardInterrupt:
    asyncio.get_running_loop().call_soon(bot.close())
