class Response:
    def __init__(self, response: str):
        self.text = response
        self.count = 1

    def __repr__(self):
        attrs = [
            ('text', self.text),
            ('count', self.count)
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'


class Question:
    def __init__(self, question: str):
        self.text = question
        self.responses = []

    def __repr__(self):
        attrs = [
            ('text', self.text),
            ('responses', self.responses)
        ]
        joined = ' '.join('%s=%r' % t for t in attrs)
        return f'<{self.__class__.__name__} {joined}>'

    def add_response(self, resp: Response):
        for response in self.responses:
            if response.text == resp.text:
                response.count += resp.count
                return
        self.responses.append(resp)
