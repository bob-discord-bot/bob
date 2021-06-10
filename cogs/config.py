import os
import bob
import qna
import json
import discord
import logging
from discord.ext import tasks
from discord.ext import commands


class Config(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.Config")
        self.config = {"guilds": {}, "optout": [], "question_limit": 100000, "blacklist": []}
        self.question_map = {}

        if os.path.exists("data.json"):
            self.logger.debug("loading questions...")
            with open("data.json") as file:
                questions = qna.json.json_to_questions(file.read())
            for question in questions:
                self.question_map.update({question.text: question})
            del questions
            self.logger.debug(f"loaded {len(self.question_map.keys())} questions.")

        if os.path.exists("config.json"):
            self.logger.debug("loading config...")
            with open("config.json") as file:
                self.config: dict = json.load(file)
                if "guilds" not in self.config.keys():
                    self.config.update({"guilds": {}})
                if "optin" not in self.config.keys():
                    self.config.update({"optin": []})
                if "optout" in self.config.keys():
                    self.config.pop("optout")
                if "question_limit" not in self.config.keys():
                    self.config.update({"question_limit": 100000})
                if "blacklist" not in self.config.keys():
                    self.config.update({"blacklist": []})

        self.logger.debug("loaded config.")

        self.periodic_data_clean_and_save.start()
        self.update_status.start()

    def save_data(self):
        with open("config.json", "w+") as file:
            json.dump(self.config, file)

        with open("data.json", "w+") as file:
            file.write(qna.json.questions_to_json(list(self.question_map.values())))

        self.logger.debug("done saving data.")

    @tasks.loop(minutes=1.0)
    async def periodic_data_clean_and_save(self):
        self.logger.debug("cleaning data...")
        removed = 0
        while len(self.question_map.values()) > self.config["question_limit"]:
            self.question_map.pop(list(self.question_map.keys())[0])
            removed += 1
        self.logger.debug("removed %d questions, saving data...", removed)
        self.save_data()

    @tasks.loop(minutes=1.0)
    async def update_status(self):
        self.logger.debug("calculating responses...")
        responses = len([response for question in self.question_map.values() for response in question.responses])

        self.logger.debug(f"{responses} responses, updating status...")
        game = discord.Activity(
            type=discord.ActivityType.playing,
            name=f"bob v{bob.__version__} // {self.client.command_prefix}help // {len(self.question_map.keys())} "
                 f"questions and {responses} responses in {len(self.client.guilds)} servers"
        )
        await self.client.change_presence(activity=game)

    def cog_unload(self):
        self.logger.debug("cog is being unloaded, saving data...")
        self.save_data()


def setup(client: commands.Bot):
    client.add_cog(Config(client))
