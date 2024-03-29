import random
import typing
import Levenshtein
import discord

from bob.db import Question, Response


async def calculate_popularity(question: Question) -> typing.Dict[Response, float]:
    popularity = {}
    total = 0
    responses = await question.responses.all()
    for response in responses:
        total += response.count
    for response in responses:
        popularity.update({response: response.count / total})
    return popularity


async def pick_response(question: Question) -> Response:
    popularity = await calculate_popularity(question)

    keys = list(popularity.keys())
    random_prob = random.random()
    pop = 0
    for response in keys:
        pop = pop + popularity[response]
        if pop > random_prob:
            return response


def get_closest_question(questions: typing.List[Question], message: str) -> Question:
    lowest = None
    target = None
    for question in questions:
        dist = Levenshtein.distance(question.text, message)
        if lowest is None or lowest > dist:
            lowest = dist
            target = question

    return target


def get_message_as_string(message: discord.Message) -> str:
    ret = message.clean_content
    ret += " " + " ".join([attachment.url for attachment in message.attachments])
    ret += " " + " ".join(
        [
            f"https://media.discordapp.net/stickers/{sticker.id}.png?size=160"
            for sticker in message.stickers
        ]
    )

    return ret.strip()
