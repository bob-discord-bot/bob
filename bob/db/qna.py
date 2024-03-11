from tortoise import fields
from tortoise.models import Model


class Question(Model):
    id = fields.IntField(pk=True)
    text = fields.TextField()
    guild = fields.BigIntField()
    channel = fields.BigIntField()
    message = fields.BigIntField()
    author = fields.BigIntField()


class Response(Model):
    id = fields.IntField(pk=True)
    text = fields.TextField()
    count = fields.IntField(default=1)
    question = fields.ForeignKeyField("bob.Question", related_name="responses")
    message = fields.BigIntField()
    author = fields.BigIntField()
