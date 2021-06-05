import os
import qna
import argparse
import discord
from discord.ext import commands, tasks
import json
import logging

version = "v2.2.1 alpha"
blue_color = 0x2273E6
red_color = 0xE82E3E

parser = argparse.ArgumentParser(description=f"bob {version}")
parser.add_argument("--debug", "-d", action="store_true", help="enable debug mode")
args = parser.parse_args()

logging.basicConfig(
    level=logging.DEBUG if args.debug else logging.INFO,
    format='[%(asctime)s / %(levelname)s] %(name)s: %(message)s'
)
client = commands.Bot(command_prefix="bc." if args.debug else "b.")
question_map = {}
config = {"guilds": {}}

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
            color=red_color
        )
        return await ctx.reply(embed=embed)

    elif isinstance(error, commands.MissingPermissions):
        perms = "\n - ".join(error.missing_perms)
        embed = discord.Embed(
            title="you're missing permissions to run this command.",
            description=f"you're missing the following permissions:\n{perms}",
            color=red_color
        )
        return await ctx.reply(embed=embed)

    elif isinstance(error, commands.NotOwner):
        embed = discord.Embed(
            title="you're missing permissions to run this command.",
            description=f"only the owner of the bot can run this command.",
            color=red_color
        )
        return await ctx.reply(embed=embed)


@client.event
async def on_ready():
    logger.info(f"bob {version} is ready!")
    periodic_data_save.start()
    update_status.start()


@client.event
async def on_disconnect():
    logger.debug("client disconnected, saving data...")
    with open("config.json", "w+") as file:
        json.dump(config, file)

    with open("data.json", "w+") as file:
        file.write(qna.json.questions_to_json(list(question_map.values())))

    logger.debug("done saving data.")


@tasks.loop(minutes=5.0)
async def periodic_data_save():
    logger.debug("saving data (periodic)...")
    with open("config.json", "w+") as file:
        json.dump(config, file)

    with open("data.json", "w+") as file:
        file.write(qna.json.questions_to_json(list(question_map.values())))

    logger.debug("done saving data.")


@tasks.loop(seconds=15.0)
async def update_status():
    logger.debug("calculating responses...")
    responses = [response for question in question_map.values() for response in question.responses]
    logger.debug(f"{len(responses)} responses, updating status...")
    game = discord.Activity(
        type=discord.ActivityType.listening,
        name=f"{len(question_map.keys())} questions and {len(responses)} responses in {len(client.guilds)} servers // "
             f"bob {version} // {client.command_prefix}help"
    )
    await client.change_presence(activity=game)


@client.event
async def on_message(message: discord.Message):
    if message.author.bot or message.is_system() or message.guild is None:
        return

    if str(message.guild.id) in config["guilds"].keys():
        if message.channel.id == config["guilds"][str(message.guild.id)]["channel"]:
            content = qna.classes.sanitize_question(message.clean_content)
            question = qna.helpers.get_closest_question(list(question_map.values()), content)
            response = qna.helpers.pick_response(question)
            try:
                await message.reply(response.text)
            except discord.errors.HTTPException:
                return
            logger.debug(f"reply: {message.clean_content} -> {response.text}")
        else:
            await client.process_commands(message)
    else:
        await client.process_commands(message)

    if message.reference:
        try:
            reply = await message.channel.fetch_message(message.reference.message_id)
        except discord.NotFound:
            return

        content = qna.classes.sanitize_question(reply.clean_content)
        if content not in question_map.keys():
            question_map.update({content: qna.classes.Question(content)})
        question_map[content].add_response(qna.classes.Response(message.clean_content))
        logger.debug(f"save: {reply.clean_content} -> {message.clean_content}")


@commands.has_permissions(manage_channels=True)
@client.command(brief="sets the channel bob should talk in")
async def channel(ctx: commands.Context, target_channel: discord.TextChannel):
    if str(ctx.guild.id) not in config["guilds"].keys():
        config["guilds"].update({str(ctx.guild.id): {"channel": target_channel.id}})
    else:
        config["guilds"][str(ctx.guild.id)]["channel"] = target_channel.id

    await ctx.reply(f"done! bob will now talk in {target_channel.mention}.")


@commands.is_owner()
@client.command()
async def stop(ctx: commands.Context):
    await ctx.reply("stopping...")
    await client.close()


@client.command(brief="invite me to your server!")
async def invite(ctx: commands.Context):
    embed = discord.Embed(
        title="here you go!",
        description=f"you can invite me to your server by [clicking on this link](https://discord.com/api/oauth2/author"
                    f"ize?client_id={client.user.id}&permissions=3072&scope=bot)",
        color=blue_color
    )
    await ctx.reply(embed=embed)


if __name__ == "__main__":
    logger.debug("loading questions...")
    with open("data.json") as file:
        questions = qna.json.json_to_questions(file.read())
    for question in questions:
        question_map.update({question.text: question})
    del questions
    logger.debug(f"loaded {len(question_map.keys())} questions")

    logger.debug("loading config...")
    if os.path.exists("config.json"):
        with open("config.json") as file:
            config = json.load(file)
            if "guilds" not in config.keys():
                config.update({"guilds": {}})

    logger.debug("connecting to discord...")
    with open("token.txt") as file:
        client.run(file.readline())
