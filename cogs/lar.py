# LaR: Learn and Reply
import qna
import discord
import logging
from cogs.config import Config
from discord.ext import commands


class LaR(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.LaR")
        self.config: Config = client.get_cog("Config")
        self.logger.debug("registered.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if (message.author.bot or message.is_system() or message.guild is None
                or message.author.id in self.config.config["blacklist"]):
            return

        # Reply
        if str(message.guild.id) in self.config.config["guilds"].keys():
            if message.channel.id == self.config.config["guilds"][str(message.guild.id)]["channel"]:
                content = qna.classes.sanitize_question(message.clean_content)
                question = qna.helpers.get_closest_question(list(self.config.question_map.values()), content)
                response = qna.helpers.pick_response(question)
                try:
                    await message.reply(response.text)
                except discord.errors.HTTPException:
                    return
                self.logger.debug(f"reply: {message.clean_content} -> {response.text}")

        # Learn
        if message.author.id in self.config.config["optout"]:
            return

        if message.reference:
            try:
                reply = await message.channel.fetch_message(message.reference.message_id)
            except discord.NotFound:
                return

            if reply.author.bot:
                return

            content = qna.classes.sanitize_question(reply.clean_content)
            if content not in self.config.question_map.keys():
                self.config.question_map.update({content: qna.classes.Question(content)})
            self.config.question_map[content].add_response(qna.classes.Response(message.clean_content))
            self.logger.debug(f"save: {reply.clean_content} -> {message.clean_content}")


def setup(client: commands.Bot):
    client.add_cog(LaR(client))
