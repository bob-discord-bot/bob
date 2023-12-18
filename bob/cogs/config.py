import os
import topgg
import bob.qna as qna
import json
import time
import asyncio
import discord
import logging
import functools
from discord.ext import tasks
from discord.ext import commands
from concurrent.futures.process import ProcessPoolExecutor


def snowflake_to_timestamp(snowflake: int):
    return ((snowflake >> 22) + 1420070400000) / 1000


class Config(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.Config")
        self.config = {
            "guilds": {},
            "optout": [],
            "question_limit": 100000,
            "blacklist": [],
            "analytics": [],
        }
        self.messages_sent = 0
        self.question_map = {}
        if os.path.exists("topgg.txt"):
            with open("topgg.txt") as file:
                self.topgg = topgg.DBLClient(
                    bot=self.client, token=file.readline().strip("\n"), autopost=True
                )

        if os.path.exists("data.json"):
            self.logger.debug("loading questions...")
            with open("data.json") as file:
                questions = qna.json.json_to_questions(file.read())
            for question in questions:
                self.question_map.update(
                    {question.text + str(question.guild): question}
                )
            del questions
            self.logger.debug("loaded %d questions.", len(self.question_map))

        if os.path.exists("config.json"):
            self.logger.debug("loading config...")
            with open("config.json") as file:
                self.config: dict = json.load(file)
                if "guilds" not in self.config.keys():
                    self.config.update({"guilds": {}})
                if "optout" not in self.config.keys():
                    self.config.update({"optout": []})
                if "optin" in self.config.keys():
                    self.config.pop("optin")
                if "question_limit" not in self.config.keys():
                    self.config.update({"question_limit": 100000})
                if "blacklist" not in self.config.keys():
                    self.config.update({"blacklist": []})
                if "analytics" not in self.config.keys():
                    self.config.update({"analytics": []})

        self.logger.debug("loaded config.")

        self.periodic_data_clean_and_save.start()
        self.update_status.start()
        self.log_data.start()

    @classmethod
    def __save_data_impl(logger, config, question_map):
        logger.debug("saving data...")

        with open("config.json", "w+") as file:
            json.dump(config, file)

        with open("data.json", "w+") as file:
            file.write(qna.json.questions_to_json(list(question_map.values())))

        logger.debug("done saving data.")

    async def save_data(self):
        with ProcessPoolExecutor(1) as executor:
            await asyncio.get_event_loop().run_in_executor(
                executor, functools.partial(self.__save_data_impl, self.logger, self.config, self.question_map)
            )

    @tasks.loop(minutes=5.0)
    async def periodic_data_clean_and_save(self):
        self.logger.debug("cleaning data...")
        removed_questions = 0
        removed_responses = 0
        while len(self.question_map.values()) > self.config["question_limit"]:
            self.question_map.pop(list(self.question_map.keys())[0])
            removed_questions += 1
        to_pop = []
        for question_key in self.question_map.keys():
            question = self.question_map[question_key]
            if question.author in self.config["blacklist"]:
                to_pop.append(question_key)
                continue

            if question.guild not in [guild.id for guild in self.client.guilds]:
                to_pop.append(question_key)
                continue

            responses_to_remove = []
            for response in question.responses:
                if response.author in self.config["blacklist"]:
                    responses_to_remove.append(response)

            for index in responses_to_remove:
                question.responses.remove(index)

            removed_responses += len(responses_to_remove)

            if len(question.responses) == 0:
                to_pop.append(question_key)

        for key in to_pop:
            self.question_map.pop(key)

        removed_questions += len(to_pop)
        self.logger.debug(
            "removed %d questions and %d responses, saving data...",
            removed_questions,
            removed_responses,
        )
        await self.save_data()

    @tasks.loop(minutes=1.0)
    async def update_status(self):
        self.logger.debug("calculating responses...")
        responses = len(
            [
                response
                for question in self.question_map.values()
                for response in question.responses
            ]
        )

        self.logger.debug(f"{responses} responses, updating status...")
        game = discord.Activity(
            type=discord.ActivityType.playing,
            name=f"with your messages | {self.client.command_prefix}help | {len(self.question_map.keys())} prompts and "
            f"{responses} responses",
        )
        await self.client.change_presence(activity=game)

    @tasks.loop(hours=24.0)
    async def log_data(self):
        self.logger.debug("calculating responses...")
        responses = len(
            [
                response
                for question in self.question_map.values()
                for response in question.responses
            ]
        )

        self.logger.debug("adding analytics info...")
        self.config["analytics"].append(
            [
                len(self.question_map),
                responses,
                len(self.client.guilds),
                time.time(),
                self.messages_sent,
            ]
        )

        self.messages_sent = 0

        if len(self.config["analytics"]) > 30:
            self.config["analytics"] = self.config["analytics"][-30:]

    def cog_unload(self):
        self.logger.debug("cog is being unloaded, saving data...")
        self.__save_data_impl(self.logger, self.config, self.question_map)  # can't async, doesn't matter


async def setup(client: commands.Bot):
    await client.add_cog(Config(client))
