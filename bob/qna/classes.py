import re
import string

PUNCTUATION_REGEX = re.compile(f"[{string.punctuation}]")


def sanitize_question(content: str) -> str:
    return PUNCTUATION_REGEX.sub("", content.lower())


class Response:
    def __init__(
        self, response: str, guild: int, channel: int, message: int, author: int
    ):
        self.text = response.strip(" \n")
        self.guild = guild
        self.channel = channel
        self.message = message
        self.author = author
        self.count = 1

    def __repr__(self):
        attrs = [("text", self.text), ("count", self.count)]
        joined = " ".join("%s=%r" % t for t in attrs)
        return f"<{self.__class__.__name__} {joined}>"


class Question:
    def __init__(
        self, question: str, guild: int, channel: int, message: int, author: int
    ):
        self.text = question
        self.guild = guild
        self.channel = channel
        self.message = message
        self.author = author
        self.responses = []

    def __repr__(self):
        attrs = [("text", self.text), ("responses", self.responses)]
        joined = " ".join("%s=%r" % t for t in attrs)
        return f"<{self.__class__.__name__} {joined}>"

    def add_response(self, resp: Response):
        for response in self.responses:
            if sanitize_question(response.text) == sanitize_question(resp.text):
                response.count += resp.count
                return
        self.responses.append(resp)
