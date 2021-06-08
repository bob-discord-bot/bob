import json
import typing
from qna.classes import Question, Response


def response_to_dict(response: Response) -> dict:
    data = {
        'text': response.text,
        'count': response.count,
        'guild': response.guild,
        'channel': response.channel,
        'message': response.message,
        'author': response.author
    }
    return data


def dict_to_response(response_dict: dict) -> Response:
    out = Response(
        response_dict['text'],
        response_dict.get("guild", 0),
        response_dict.get("channel", 0),
        response_dict.get("message", 0),
        response_dict.get("author", 0)
    )
    out.count = response_dict['count']
    return out


def question_to_dict(question: Question) -> dict:
    data = {
        'text': question.text,
        'responses': [],
        'guild': question.guild,
        'channel': question.channel,
        'message': question.message,
        'author': question.author
    }
    for response in question.responses:
        data['responses'].append(response_to_dict(response))

    return data


def dict_to_question(question_dict: dict) -> Question:
    out = Question(
        question_dict['text'],
        question_dict.get("guild", 0),
        question_dict.get("channel", 0),
        question_dict.get("message", 0),
        question_dict.get("author", 0)
    )
    for response in question_dict['responses']:
        out.add_response(dict_to_response(response))
    return out


def questions_to_json(questions: typing.List[Question]) -> str:
    out = []
    for question in questions:
        out.append(question_to_dict(question))

    return json.dumps(out, separators=(',', ':'))


def json_to_questions(questions_json: str) -> typing.List[Question]:
    questions_list = json.loads(questions_json)
    out = []
    for question in questions_list:
        out.append(dict_to_question(question))
    return out
