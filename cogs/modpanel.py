import bob
import logging
import requests
import threading
import subprocess
import nest_asyncio
from cogs.config import Config
from discord.ext import commands
from flask import Flask, render_template, request, redirect


class ModPanel(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.ModPanel")
        self.logger.debug("registered.")
        self.config: Config = client.get_cog("Config")
        self.app = Flask("ModPanel")
        nest_asyncio.apply(self.client.loop)

        @self.app.route("/")
        def index():
            self.logger.debug("calculating responses...")
            responses = len([response for question in self.config.question_map.values()
                             for response in question.responses])
            self.logger.debug("%d responses", responses)
            return render_template(
                "index.html",
                bob_version=bob.__version__,
                questions=len(self.config.question_map.keys()),
                responses=responses,
                guilds=len(self.client.guilds),
                users=len(self.config.config["optin"]),
                shards=self.client.shard_count
            )

        @self.app.route("/questions")
        def question_list():
            questions_list = list(self.config.question_map.values())
            questions = {k: questions_list[k] for k in range(len(questions_list))}
            search = request.args.get('search')
            if search:
                questions = {k: v for k, v in questions.items() if search in v.text}
            return render_template(
                "question_list.html",
                bob_version=bob.__version__,
                questions=questions
            )

        @self.app.route("/question/<question_id>", methods=["GET", "DELETE"])
        def question_manage(question_id):
            question_id = int(question_id)
            question_key = list(self.config.question_map.keys())[question_id]
            if request.method == "GET":
                question = self.config.question_map[question_key]
                return render_template(
                    "question_manage.html",
                    bob_version=bob.__version__,
                    question=question,
                    id=question_id
                )
            elif request.method == "DELETE":
                self.config.question_map.pop(question_key)
                return "", 204

        @self.app.route("/question/<question_id>/response/<response_id>", methods=["DELETE"])
        def delete_response_from_response(question_id, response_id):
            question_id = int(question_id)
            response_id = int(response_id)
            question_key = list(self.config.question_map.keys())[question_id]
            self.config.question_map[question_key].responses.pop(response_id)
            return "", 204

        @self.app.route("/responses")
        def response_list():
            questions_list = list(self.config.question_map.values())
            questions = {k: questions_list[k] for k in range(len(questions_list))}
            search = request.args.get('search')
            if search:
                questions = {k: v for k, v in questions.items() for response in v.responses if search in response.text}
            return render_template(
                "response_list.html",
                bob_version=bob.__version__,
                questions=questions
            )

        @self.app.route("/blacklist", methods=["GET", "POST"])
        def blacklist():
            if request.method == "GET":
                return render_template(
                    "blacklist.html",
                    bob_version=bob.__version__,
                    blacklist=self.config.config["blacklist"]
                )
            elif request.method == "POST":
                self.config.config["blacklist"].append(int(request.form["id"]))
                return redirect("/blacklist")

        @self.app.route("/blacklist/<userid>", methods=["DELETE"])
        def delete_from_blacklist(userid):
            userid = int(userid)
            self.config.config["blacklist"].remove(userid)
            return "", 204

        @self.app.route("/maintenance")
        def maintenance():
            releases = requests.get("https://api.github.com/repos/omaemae/bob/releases").json()

            return render_template(
                "maintenance.html",
                bob_version=bob.__version__,
                latest_version=releases[0]["name"],
                out_of_date=releases[0]["name"] != "v" + bob.__version__
            )

        @self.app.route("/maintenance/stop")
        def stop():
            self.client.loop.run_until_complete(self.client.close())
            return "", 204

        @self.app.route("/maintenance/update")
        def update():
            subprocess.run(["git", "pull"])
            subprocess.run(["pip", "install", "-r", "requirements.txt"])
            self.client.loop.run_until_complete(self.client.close())
            return "", 204

        self.process = threading.Thread(
            target=self.app.run,
            kwargs={"host": "127.0.0.1", "port": 8540},
            daemon=True
        )
        self.process.start()


def setup(client: commands.Bot):
    client.add_cog(ModPanel(client))
