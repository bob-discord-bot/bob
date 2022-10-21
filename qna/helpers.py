import random
import typing
import Levenshtein
from .classes import Question, Response


def calculate_popularity(question: Question) -> typing.Dict[Response, float]:
    popularity = {}
    total = 0
    for response in question.responses:
        total += response.count
    for response in question.responses:
        popularity.update({response: response.count / total})
    return popularity


def pick_response(question: Question) -> Response:
    popularity = calculate_popularity(question)

    keys = list(popularity.keys())
    random_prob = random.random()
    pop = 0
    for response in keys:
        pop = pop + popularity[response]
        if pop > random_prob:
            return response


def get_closest_question(questions: typing.List[Question], message: str, guild_id: int) -> Question:
    lowest = None
    target = None
    for question in questions:
        dist = Levenshtein.distance(question.text, message)
        if lowest is None or lowest > dist:
            lowest = dist
            target = question

    return target
