import bob
import qna
import json
import discord
import logging
from discord.ext import tasks
from discord.ext import commands


class Events(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.Events")
        self.periodic_data_save.start()
        self.update_status.start()
        self.logger.debug("registered.")

    def save_data(self):
        with open("config.json", "w+") as file:
            json.dump(bob.config, file)

        with open("data.json", "w+") as file:
            file.write(qna.json.questions_to_json(list(bob.question_map.values())))

        self.logger.debug("done saving data.")

    # FIXME: not triggered by d.py, find different way of triggering this
    @commands.Cog.listener()
    async def on_disconnect(self):
        self.logger.debug("client disconnected, saving data...")
        self.save_data()

    @tasks.loop(minutes=5.0)
    async def periodic_data_save(self):
        self.logger.debug("saving data (periodic)...")
        self.save_data()

    @tasks.loop(seconds=15.0)
    async def update_status(self):
        self.logger.debug("calculating responses...")
        responses = [response for question in bob.question_map.values() for response in question.responses]

        self.logger.debug(f"{len(responses)} responses, updating status...")
        game = discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{len(bob.question_map.keys())} questions and {len(responses)} responses in "
                 f"{len(self.client.guilds)} servers // bob {bob.__version__} // {self.client.command_prefix}help"
        )
        await self.client.change_presence(activity=game)


def setup(client: commands.Bot):
    client.add_cog(Events(client))
