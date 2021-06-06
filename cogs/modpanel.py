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

        self.app = Flask("ModPanel")

        @self.app.route("/")
        def index():
            self.logger.debug("calculating responses...")
            config: Config = client.get_cog("Config")
            responses = len([response for question in config.question_map.values()
                             for response in question.responses])
            self.logger.debug("%d responses", responses)
            return render_template(
                'index.html',
                bob_version=bob.__version__,
                questions=len(config.question_map.keys()),
                responses=responses,
                guilds=len(self.client.guilds),
                users=len(self.client.users),
                shards=self.client.shard_count
            )

        self.process = threading.Thread(
            target=self.app.run,
            kwargs={"host": "127.0.0.1", "port": 8540},
            daemon=True
        )
        self.process.start()


def setup(client: commands.Bot):
    client.add_cog(ModPanel(client))
