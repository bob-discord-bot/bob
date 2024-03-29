import os.path
import random
import string
import typing

import bob
import logging
import threading
import subprocess
import nest_asyncio

import bob.qna.json
from bob.cogs.config import Config
from discord.ext import commands

from flask_cors import CORS
from flask import Flask, jsonify, request


class WebAPI(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.WebAPI")
        self.logger.debug("registered.")
        self.config: typing.Union[Config, None] = client.get_cog("Config")
        self.app = Flask("WebAPI")
        self.login_key = ""
        if os.path.exists(".login_key"):
            with open(".login_key") as file:
                self.login_key = file.read().strip()
        CORS(self.app)
        nest_asyncio.apply(self.client.loop)

        """
        Publicly available bot information, such as version, question count, response count, guilds, etc.
        """

        @self.app.route("/api/bot_info")
        def bot_info():
            responses = len(
                [
                    response
                    for question in self.config.question_map.values()
                    for response in question.responses
                ]
            )
            return {
                "version": bob.__version__,
                "questions": len(self.config.question_map.keys()),
                "responses": responses,
                "guilds": len(self.client.guilds),
            }

        """
        Initiates the login procedure.
        """

        @self.app.route("/api/auth/start", methods=["POST"])
        def auth_start():
            self.login_key = "".join(
                random.choices(
                    string.ascii_letters + string.digits + string.punctuation, k=128
                )
            )
            with open(".login_key", "w+") as login_key:
                login_key.write(self.login_key + "\n")
            return ""

        def auth_check():
            return request.headers.get("Authorization") == self.login_key

        """
        Checks if login key is valid.
        """

        @self.app.route("/api/auth/check")
        def auth_check_route():
            if not auth_check():
                return "", 400
            return ""

        """
        Returns questions.
        
        | QS parameter    | Required? | Use                      |
        | --------------- | --------- | ------------------------ |
        | search          | false     | Search through questions |
        | response_search | false     | Search through responses |
        | start           | false     | Skip X questions         |
        | count           | false     | Return X questions       |
        
        For use in dashboard, requires authentication.
        """

        @self.app.route("/api/questions")
        def question_list():
            if not auth_check():
                return "", 400
            questions_list = bob.qna.json.questions_to_list(
                self.config.question_map.values(), encrypt=False, to_str=True
            )
            questions = {k: v for k, v in enumerate(questions_list)}
            search = request.args.get("search")
            response_search = request.args.get("response_search")
            start = request.args.get("start")
            count = request.args.get("count")
            if search:
                questions = {i: q for i, q in questions.items() if search in q["text"]}
            if response_search:
                questions = {
                    i: q
                    for i, q in questions.items()
                    for r in q["responses"]
                    if response_search in r["text"]
                }
            start = int(start) if start else None
            count = int(count) if count else None
            end = start + count if start is not None and count is not None else count
            questions = {i: q for i, q in list(questions.items())[start:end]}
            return questions

        """
        Returns data for a question.
        
        For use in dashboard, requires authentication.
        """

        @self.app.route("/api/questions/<question_id>")
        def question_info(question_id):
            if not auth_check():
                return "", 400
            question_id = int(question_id)
            question_key = list(self.config.question_map.keys())[question_id]
            return bob.qna.json.question_to_dict(
                self.config.question_map[question_key], encrypt=False, to_str=True
            )

        """
        Deletes a question.

        For use in dashboard, requires authentication.
        """

        @self.app.route("/api/questions/<question_id>", methods=["DELETE"])
        def question_delete(question_id):
            if not auth_check():
                return "", 400
            question_id = int(question_id)
            question_key = list(self.config.question_map.keys())[question_id]
            self.config.question_map.pop(question_key)
            return "", 204

        """
        Deletes a response from a question.

        For use in dashboard, requires authentication.
        """

        @self.app.route(
            "/api/questions/<question_id>/responses/<response_id>", methods=["DELETE"]
        )
        def delete_response_from_question(question_id, response_id):
            if not auth_check():
                return "", 400
            question_id = int(question_id)
            response_id = int(response_id)
            question_key = list(self.config.question_map.keys())[question_id]
            self.config.question_map[question_key].responses.pop(response_id)
            return "", 204

        """
        Lists blacklisted IDs.

        For use in dashboard, requires authentication.
        """

        @self.app.route("/api/blacklist")
        def blacklist():
            if not auth_check():
                return "", 400
            return jsonify(
                [
                    str(blacklisted_id)
                    for blacklisted_id in self.config.config["blacklist"]
                ]
            )

        """
        Adds a new ID to the blacklist.

        For use in dashboard, requires authentication.
        """

        @self.app.route("/api/blacklist", methods=["POST"])
        def add_to_blacklist():
            if not auth_check():
                return "", 400
            data = request.get_json()
            self.config.config["blacklist"].append(int(data["id"]))
            return "", 204

        """
        Remove ID from the blacklist.

        For use in dashboard, requires authentication.
        """

        @self.app.route("/api/blacklist/<userid>", methods=["DELETE"])
        def delete_from_blacklist(userid):
            if not auth_check():
                return "", 400
            userid = int(userid)
            self.config.config["blacklist"].remove(userid)
            return "", 204

        """
        Stops bob.
        
        In production, bob will be running as a service, effectively restarting the bot.

        For use in dashboard, requires authentication.
        """

        @self.app.route("/api/maintenance/stop")
        def stop():
            if not auth_check():
                return "", 400
            self.client.loop.run_until_complete(self.client.close())
            return "", 204

        """
        Updates and stops bob.

        In production, bob will be running as a service, effectively restarting the bot.

        For use in dashboard, requires authentication.
        """

        @self.app.route("/api/maintenance/update")
        def update():
            if not auth_check():
                return "", 400
            subprocess.run(["git", "pull"])
            subprocess.run(["pip", "install", "-r", "requirements.txt"])
            self.client.loop.run_until_complete(self.client.close())
            return "", 204

        self.process = threading.Thread(
            target=self.app.run, kwargs={"host": "127.0.0.1", "port": 8540}, daemon=True
        )
        self.process.start()


async def setup(client: commands.Bot):
    await client.add_cog(WebAPI(client))
