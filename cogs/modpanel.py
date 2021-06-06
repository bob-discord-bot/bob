import bob
import logging
import threading
from cogs.config import Config
from discord.ext import commands
from flask import Flask, render_template


class ModPanel(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.ModPanel")
        self.logger.debug("registered.")
        self.config: Config = client.get_cog("Config")
        self.app = Flask("ModPanel")

        @self.app.route("/")
        def index():
            self.logger.debug("calculating responses...")
            responses = len([response for question in self.config.question_map.values()
                             for response in question.responses])
            self.logger.debug("%d responses", responses)
            return render_template(
                'index.html',
                bob_version=bob.__version__,
                questions=len(self.config.question_map.keys()),
                responses=responses,
                guilds=len(self.client.guilds),
                users=len(self.client.users),
                shards=self.client.shard_count
            )

        @self.app.route("/questions")
        def question_list():
            return render_template(
                'question_list.html',
                bob_version=bob.__version__,
                questions=list(self.config.question_map.values())
            )

        @self.app.route("/question/<question_id>")
        def question_manage(question_id):
            question_id = int(question_id)
            question_key = list(self.config.question_map.keys())[question_id]
            question = self.config.question_map[question_key]
            return render_template(
                'question_manage.html',
                bob_version=bob.__version__,
                question=question,
                id=question_id
            )

        self.process = threading.Thread(
            target=self.app.run,
            kwargs={"host": "127.0.0.1", "port": 8540},
            daemon=True
        )
        self.process.start()


def setup(client: commands.Bot):
    client.add_cog(ModPanel(client))
