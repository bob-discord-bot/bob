import os
import bob
import qna
import json
import discord
import logging
import argparse
from discord.ext import commands

parser = argparse.ArgumentParser(description=f"bob {bob.__version__}")
parser.add_argument("--debug", "-d", action="store_true", help="enable debug mode")
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format='[%(asctime)s / %(levelname)s] %(name)s: %(message)s'
)
client = commands.AutoShardedBot(command_prefix="bc." if args.debug else "b.", help_command=None)

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
            title="you're missing a required argument!",
            description="check help for details.",
            color=bob.red_color
        )
        return await ctx.reply(embed=embed)

    elif isinstance(error, commands.BadArgument):
        embed = discord.Embed(
            title="i don't think that's correct...",
            description=str(error),
            color=bob.red_color
        )
        return await ctx.reply(embed=embed)

    elif isinstance(error, commands.MissingPermissions):
        perms = "\n - ".join(error.missing_perms)
        embed = discord.Embed(
            title="you're missing permissions to run this command.",
            description=f"you're missing the following permissions:\n{perms}",
            color=bob.red_color
        )
        return await ctx.reply(embed=embed)

    elif isinstance(error, commands.NotOwner):
        embed = discord.Embed(
            title="you're missing permissions to run this command.",
            description=f"only the owner of the bot can run this command.",
            color=bob.red_color
        )
        return await ctx.reply(embed=embed)


@client.event
async def on_ready():
    client.load_extension("cogs.events")
    client.load_extension("cogs.lar")
    client.load_extension("cogs.maintenance")
    client.load_extension("cogs.configuration")
    client.load_extension("cogs.help")
    client.load_extension("cogs.optout")
    client.load_extension("cogs.modpanel")
    logger.info(f"bob {bob.__version__} is ready!")


@client.event
async def on_message(message: discord.Message):
    if message.author.bot or message.is_system() or message.guild is None:
        return

    if str(message.guild.id) in bob.config["guilds"].keys():
        if not message.channel.id == bob.config["guilds"][str(message.guild.id)]["channel"]:
            await client.process_commands(message)
    else:
        await client.process_commands(message)

if __name__ == "__main__":
    logger.debug("loading questions...")
    with open("data.json") as file:
        questions = qna.json.json_to_questions(file.read())
    for question in questions:
        bob.question_map.update({question.text: question})
    del questions
    logger.debug(f"loaded {len(bob.question_map.keys())} questions")

    logger.debug("loading config...")
    if os.path.exists("config.json"):
        with open("config.json") as file:
            bob.config = json.load(file)
            if "guilds" not in bob.config.keys():
                bob.config.update({"guilds": {}})
            if "optout" not in bob.config.keys():
                bob.config.update({"optout": []})
            if "question_limit" not in bob.config.keys():
                bob.config.update({"question_limit": 100000})

    logger.debug("connecting to discord...")
    with open("token.txt") as file:
        client.run(file.readline())
