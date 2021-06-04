from qna import helpers, json, classes
import argparse
import discord
from configreader import config

version = 'v2.2.0 beta'

parser = argparse.ArgumentParser(description=f'bob {version}')
parser.add_argument('--debug', '-d', action='store_true', help='enable debug mode')
parser.add_argument('--version', '-v', action='version', version=version)
args = parser.parse_args()

channel_id = config["debug_channel"] if args.debug else config["target_channel"]
client = discord.Client()
questions = []


def debug(*arg, **kwargs):
    if args.debug:
        print(*arg, **kwargs)


async def debug_send(message: discord.Message, *arg, **kwargs):
    if args.debug:
        await message.channel.send(*arg, **kwargs)


@client.event
async def on_ready():
    print(f'bob {version} is ready!')
    channel = client.get_channel(channel_id)
    await channel.send(f'ℹ️ **bob {version} is ready** with {len(questions)} questions in the dataset')
    await channel.edit(topic=f'**bob {version}** | trained on {len(questions)} questions')


@client.event
async def on_message(message: discord.Message):
    if message.channel.id != channel_id:
        return
    if message.author.bot:
        return
    content = classes.sanitize_question(message.clean_content)
    if message.is_system():
        content = classes.sanitize_question(message.system_content)
    question = helpers.get_closest_question(questions, content)
    response = helpers.pick_response(question)
    debug(question)
    debug(content, '->', response.text)
    embed = discord.Embed(title="Details", color=0x2273e6)
    embed.add_field(name="Matched Question", value=question.text)
    embed.add_field(name="# of Responses", value=len(question.responses))
    try:
        await message.reply(response.text, embed=embed)
    except discord.errors.HTTPException:
        await message.channel.send(response.text, embed=embed)


if __name__ == '__main__':
    debug('initializing...')
    with open('data.json') as file:
        questions = json.json_to_questions(file.read())
    debug('loaded', len(questions), 'questions')

    with open('token.txt') as file:
        client.run(file.readline())
