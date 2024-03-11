from tortoise import fields
from tortoise.models import Model


class Guild(Model):
    guildId = fields.BigIntField(pk=True, generated=False)
    channelId = fields.BigIntField()
