import json
import typing
from qna.classes import Question, Response


def response_to_dict(response: Response) -> dict:
    data = {
        'text': response.text,
        'count': response.count
    }
    return data


def dict_to_response(response_dict: dict) -> Response:
    out = Response(response_dict['text'])
    out.count = response_dict['count']
    return out


def question_to_dict(question: Question) -> dict:
    data = {
        'text': question.text,
        'responses': []
    }
    for response in question.responses:
        data['responses'].append(response_to_dict(response))

    return data


def dict_to_question(question_dict: dict) -> Question:
    out = Question(question_dict['text'])
    for response in question_dict['responses']:
        out.add_response(dict_to_response(response))
    return out


def questions_to_json(questions: typing.List[Question]) -> str:
    out = []
    for question in questions:
        out.append(question_to_dict(question))

    return json.dumps(out, indent='\t')


def json_to_questions(questions_json: str) -> typing.List[Question]:
    questions_list = json.loads(questions_json)
    out = []
    for question in questions_list:
        out.append(dict_to_question(question))
    return out
