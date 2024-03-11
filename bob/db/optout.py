from tortoise import fields
from tortoise.models import Model


class OptOutEntry(Model):
    userId = fields.BigIntField(pk=True, generated=False)
