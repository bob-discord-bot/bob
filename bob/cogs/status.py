import logging
import discord
from topgg import DBLClient
from bob import config
from bob.db import Question, Response
from discord.ext import commands, tasks


class Status(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.Status")
        self.logger.debug("registered.")
        self.client.event(self.on_ready)

        if config.get("topggToken") is not None:
            self.topgg = DBLClient(
                bot=self.client,
                token=config.get("topggToken"),
                autopost=True,
            )
        else:
            self.logger.info("topgg token missing, not creating DBLClient")

    async def on_ready(self):
        self.update_status.start()

    @tasks.loop(minutes=5.0)
    async def update_status(self):
        question_count = await Question.all().count()
        response_count = await Response.all().count()
        game = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"you type | {self.client.command_prefix}help | {question_count} prompts and {response_count} responses",
        )
        await self.client.change_presence(activity=game)


async def setup(client: commands.Bot):
    await client.add_cog(Status(client))
