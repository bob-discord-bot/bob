from tortoise import fields
from tortoise.models import Model


class Blacklist(Model):
    userId = fields.BigIntField(pk=True, generated=False)
    reason = fields.TextField(null=True)
