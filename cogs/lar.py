# LaR: Learn and Reply
import qna
import asyncio
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

    async def learn(self, message: discord.Message):
        if message.author.id not in self.config.config["optin"] or message.author.id in self.config.config["blacklist"]:
            return

        if message.reference:
            try:
                reply: discord.Message = await message.channel.fetch_message(message.reference.message_id)
            except discord.NotFound:
                return

            if reply.author.id not in self.config.config["optin"]:
                return

            content = qna.classes.sanitize_question(reply.clean_content) + " " + \
                " ".join([attachment.url for attachment in reply.attachments])
            if content not in self.config.question_map.keys():
                self.config.question_map.update({content: qna.classes.Question(
                    content,
                    reply.guild.id,
                    reply.channel.id,
                    reply.id,
                    reply.author.id
                )})
            response_content = message.clean_content + " " + \
                " ".join([attachment.url for attachment in message.attachments])
            self.config.question_map[content].add_response(qna.classes.Response(
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
                content = qna.classes.sanitize_question(message.clean_content)
                question = qna.helpers.get_closest_question(list(self.config.question_map.values()), content)
                response = qna.helpers.pick_response(question)

                async with channel.typing():
                    text = response.text or "i don't know what to say"
                    await asyncio.sleep(min(len(text) / 50, 10))
                    await message.reply(text)
                    self.logger.debug(f"reply: {message.clean_content} -> {response.text}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.is_system() or message.guild is None or message.content.startswith("//"):
            return

        await self.learn(message)
        await self.reply(message)


def setup(client: commands.Bot):
    client.add_cog(LaR(client))
