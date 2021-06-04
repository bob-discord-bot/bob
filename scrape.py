import discord
from qna.classes import Question, Response, sanitize_question
from qna import json
from configreader import config

client = discord.Client()
limit = config["scrape_amount"]


@client.event
async def on_ready():
    questions = {}
    chat = client.get_channel(config["scrape_channel"])
    print('> Scraping...')
    count = 0  # this is lowkey better ngl
    async for message in chat.history(limit=None):
        if message.is_system():
            continue  # we don't want to deal with these
        if count >= limit:
            with open('data.json', 'w+') as file:
                file.write(json.questions_to_json(list(questions.values())))
            await client.close()
            print('\n> Done.')
            return
        if message.reference:
            try:
                reply: discord.Message = await chat.fetch_message(message.reference.message_id)
            except discord.errors.NotFound:
                continue  # too bad!!!
            content = sanitize_question(reply.clean_content)
            if content not in questions.keys():
                questions.update({content: Question(content)})
            questions[content].add_response(Response(message.clean_content))
            print(content, '->', message.clean_content)
        else:
            continue  # worthless junk
        count += 1
        print(count, '/', limit)
        # print(questions)


if __name__ == '__main__':
    with open('token.txt') as token:
        client.run(token.readline())
