# LaR: Learn and Reply
import typing

import qna
import discord
import logging
from cogs.config import Config
from discord.ext import commands


class LaR(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.LaR")
        self.config: typing.Union[Config, None] = client.get_cog("Config")
        self.logger.debug("registered.")

    async def learn(self, message: discord.Message):
        if message.author.id in self.config.config["optout"] or message.author.id in self.config.config["blacklist"]:
            return

        if message.reference:
            try:
                reply: discord.Message = await message.channel.fetch_message(message.reference.message_id)
            except discord.NotFound:
                return

            if reply.author.id in self.config.config["optout"]:
                return

            content = qna.classes.sanitize_question(reply.clean_content + " " +
                                                    " ".join([attachment.url for attachment in reply.attachments]))
            if content + str(message.guild.id) not in self.config.question_map.keys():
                self.config.question_map.update({content + str(message.guild.id): qna.classes.Question(
                    content,
                    reply.guild.id,
                    reply.channel.id,
                    reply.id,
                    reply.author.id
                )})
            response_content = (message.clean_content + " " +
                                " ".join([attachment.url for attachment in message.attachments]))
            self.config.question_map[content + str(message.guild.id)].add_response(qna.classes.Response(
                response_content,
                message.guild.id,
                message.channel.id,
                message.id,
                message.author.id
            ))
            self.logger.debug(f"save: {reply.clean_content} -> {message.clean_content}")

    async def reply(self, message: discord.Message):
        guild: discord.Guild = message.guild
        channel: discord.TextChannel = message.channel

        if str(guild.id) in self.config.config["guilds"].keys():
            if channel.id == self.config.config["guilds"][str(guild.id)]["channel"]:
                content = qna.classes.sanitize_question(str(message.clean_content))
                placeholder = "i don't know what to say"
                text = placeholder
                server_questions = [q for q in self.config.question_map.values() if q.guild == message.guild.id]
                if len(server_questions):
                    question = qna.helpers.get_closest_question(server_questions, content,
                                                                message.guild.id)
                    response = qna.helpers.pick_response(question)
                    text = response.text or placeholder
                if message.content.startswith(self.client.command_prefix):
                    text += "\n(psst, i don't listen to commands here! if you want to run a command, " \
                            "go to another channel.)"
                await message.reply(text)
                self.logger.debug(f"reply: {message.clean_content} -> {text}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.is_system() or message.guild is None:
            return

        await self.learn(message)
        await self.reply(message)


async def setup(client: commands.Bot):
    await client.add_cog(LaR(client))
