import os
import qna
import argparse
import discord
from discord.ext import commands, tasks
import json

version = "v2.2.0 alpha"

parser = argparse.ArgumentParser(description=f"bob {version}")
parser.add_argument("--debug", "-d", action="store_true", help="enable debug mode (currently unused)")
args = parser.parse_args()

client = commands.Bot(command_prefix="bob.")
question_map = {}
config = {"guilds": {}}


@client.event
async def on_ready():
    print(f"bob {version} is ready!")
    periodic_data_save.start()
    update_status.start()


@client.event
async def on_disconnect():
    print(f"client disconnected, saving data...", end=" ")
    with open("config.json", "w+") as file:
        json.dump(config, file)

    with open("data.json", "w+") as file:
        file.write(qna.json.questions_to_json(list(question_map.values())))

    print("done.")


@tasks.loop(minutes=5.0)
async def periodic_data_save():
    print(f"saving data...", end=" ")
    with open("config.json", "w+") as file:
        json.dump(config, file)

    with open("data.json", "w+") as file:
        file.write(qna.json.questions_to_json(list(question_map.values())))

    print("done.")


@tasks.loop(seconds=15.0)
async def update_status():
    game = discord.Activity(
        type=discord.ActivityType.listening,
        name=f"{len(question_map.keys())} questions // bob.help"
    )
    await client.change_presence(activity=game)


@client.event
async def on_message(message: discord.Message):
    if message.author.bot or message.is_system() or message.guild is None:
        return

    await client.process_commands(message)

    if str(message.guild.id) in config["guilds"].keys():
        if message.channel.id == config["guilds"][str(message.guild.id)]["channel"]:
            content = qna.classes.sanitize_question(message.clean_content)
            question = qna.helpers.get_closest_question(list(question_map.values()), content)
            response = qna.helpers.pick_response(question)
            try:
                await message.reply(response.text)
            except discord.errors.HTTPException:
                return

    if message.reference:
        try:
            reply = await message.channel.fetch_message(message.reference.message_id)
        except discord.NotFound:
            return

        content = qna.classes.sanitize_question(reply.clean_content)
        if content not in question_map.keys():
            question_map.update({content: qna.classes.Question(content)})
        question_map[content].add_response(qna.classes.Response(message.clean_content))
        print(content, '->', message.clean_content)


@commands.has_permissions(manage_channels=True)
@client.command()
async def channel(ctx: commands.Context, target_channel: discord.TextChannel):
    if str(ctx.guild.id) not in config["guilds"].keys():
        config["guilds"].update({str(ctx.guild.id): {"channel": target_channel.id}})
    else:
        config["guilds"][str(ctx.guild.id)]["channel"] = target_channel.id

    await ctx.reply(f"done! bob will now talk in {target_channel.mention}.")


@commands.is_owner()
@client.command()
async def stop(ctx: commands.Context):
    await client.close()


if __name__ == "__main__":
    print("loading questions...")
    with open("data.json") as file:
        questions = qna.json.json_to_questions(file.read())
    for question in questions:
        question_map.update({question.text: question})
    del questions
    print("loaded", len(question_map.keys()), "questions")

    print("loading config...")
    if os.path.exists("config.json"):
        with open("config.json") as file:
            config = json.load(file)
            if "guilds" not in config.keys():
                config.update({"guilds": {}})

    print("connecting to discord...")
    with open("token.txt") as file:
        client.run(file.readline())
