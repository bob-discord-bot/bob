import typing

import bob
import discord
import logging
import argparse
import traceback
from discord.ext import commands

from cogs.config import Config

parser = argparse.ArgumentParser(description=f"bob {bob.__version__}")
parser.add_argument("--debug", "-d", action="store_true", help="enable debug mode")
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format='[%(asctime)s / %(levelname)s] %(name)s: %(message)s'
)

intents = discord.Intents.default()
intents.message_content = True
client = commands.AutoShardedBot(command_prefix="bc." if args.debug else "b.", help_command=None,
                                 intents=intents)

logger = logging.getLogger("bob")


@client.event
async def on_command_error(ctx: commands.Context, error):
    if hasattr(ctx.command, 'on_error'):
        return

    ignored = (commands.CommandNotFound,)

    error = getattr(error, 'original', error)

    if isinstance(error, ignored):
        return

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title="You're missing a required argument!",
            description="Check help for details.",
            color=discord.Color.red()
        )
        return await ctx.reply(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="I don't think that's correct...",
            description=str(error),
            color=discord.Color.red()
        )
        return await ctx.reply(embed=embed)

    elif isinstance(error, commands.MissingPermissions):
        perms = "\n - ".join(error.missing_permissions)
        embed = discord.Embed(
            title="You're missing permissions to run this command.",
            description=f"You're missing the following permissions:\n{perms}",
            color=discord.Color.red()
        )
        return await ctx.reply(embed=embed)

    elif isinstance(error, commands.NotOwner):
        embed = discord.Embed(
            title="You're missing permissions to run this command.",
            description=f"Only the bot owner can run this command.",
            color=discord.Color.red()
        )
        return await ctx.reply(embed=embed)

    elif isinstance(error, commands.CheckFailure):
        embed = discord.Embed(
            title="You're not able to run this command.",
            description="If you're trying to opt-in, this usually means you are already opted-in.",
            color=discord.Color.red()
        )
        return await ctx.reply(embed=embed)

    else:
        error: Exception
        traceback.print_exception(type(error), error, error.__traceback__)


@client.event
async def on_ready():
    cogs = [
        "cogs.config",
        "cogs.lar",
        "cogs.configuration",
        "cogs.optin",
        "cogs.usercommands",
        "cogs.help",
        "cogs.webapi",
        "jishaku"
    ]
    for cog in cogs:
        await client.load_extension(cog)
    logger.info(f"bob v{bob.__version__} is ready!")


@client.event
async def on_message(message: discord.Message):
    config: typing.Union[Config, None] = client.get_cog("Config")
    if message.author.bot or message.is_system() or message.guild is None:
        return

    if str(message.guild.id) in config.config["guilds"].keys():
        if not message.channel.id == config.config["guilds"][str(message.guild.id)]["channel"]:
            await client.process_commands(message)
    else:
        await client.process_commands(message)

if __name__ == "__main__":
    logger.debug("connecting to discord...")
    with open("token.txt") as file:
        client.run(file.readline())
