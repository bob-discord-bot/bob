import json
import base64
import logging
import typing
import os.path
import nacl.utils
import nacl.secret

from bob.qna.classes import Question, Response

logger = logging.getLogger("qna.json")

uses_encryption = True
if not os.path.exists(".key"):
    logger.debug(
        "Didn't find key, assuming data is not encrypted. Will encrypt when saving."
    )
    uses_encryption = False
    key: bytes = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    with open(".key", "wb+") as file:
        file.write(key)
else:
    with open(".key", "rb") as file:
        key = file.read()

box = nacl.secret.SecretBox(key)


def if_str(value, to_str: bool):
    return str(value) if to_str else value


def response_to_dict(response: Response, encrypt=True, to_str=False) -> dict:
    data = {
        "text": base64.b64encode(box.encrypt(response.text.encode())).decode()
        if encrypt
        else response.text,
        "count": response.count,
        "guild": if_str(response.guild, to_str),
        "channel": if_str(response.channel, to_str),
        "message": if_str(response.message, to_str),
        "author": if_str(response.author, to_str),
    }
    return data


def dict_to_response(response_dict: dict) -> Response:
    out = Response(
        (
            box.decrypt(base64.b64decode(response_dict["text"].encode())).decode()
            if uses_encryption
            else response_dict["text"]
        ),
        response_dict.get("guild", 0),
        response_dict.get("channel", 0),
        response_dict.get("message", 0),
        response_dict.get("author", 0),
    )
    out.count = response_dict["count"]
    return out


def question_to_dict(question: Question, encrypt=True, to_str=False) -> dict:
    data = {
        "text": base64.b64encode(box.encrypt(question.text.encode())).decode()
        if encrypt
        else question.text,
        "responses": [],
        "guild": if_str(question.guild, to_str),
        "channel": if_str(question.channel, to_str),
        "message": if_str(question.message, to_str),
        "author": if_str(question.author, to_str),
    }
    for response in question.responses:
        data["responses"].append(
            response_to_dict(response, encrypt=encrypt, to_str=to_str)
        )

    return data


def dict_to_question(question_dict: dict) -> Question:
    out = Question(
        (
            box.decrypt(base64.b64decode(question_dict["text"].encode())).decode()
            if uses_encryption
            else question_dict["text"]
        ),
        question_dict.get("guild", 0),
        question_dict.get("channel", 0),
        question_dict.get("message", 0),
        question_dict.get("author", 0),
    )
    for response in question_dict["responses"]:
        out.add_response(dict_to_response(response))
    return out


def questions_to_list(
    questions: typing.List[Question], encrypt=True, to_str=False
) -> typing.List[dict]:
    out = []
    for question in questions:
        out.append(question_to_dict(question, encrypt=encrypt, to_str=to_str))

    return out


def questions_to_json(questions: typing.List[Question]) -> str:
    out = questions_to_list(questions)
    return json.dumps(out, separators=(",", ":"))


def json_to_questions(questions_json: str) -> typing.List[Question]:
    questions_list = json.loads(questions_json)
    out = []
    for question in questions_list:
        out.append(dict_to_question(question))
    return out
