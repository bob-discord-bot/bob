# LaR: Learn and Reply
import bob.qna
import discord
import logging
from bob.cogs.modmode import DeleteView, ModMode
from bob.cogs.config import Config
from discord.ext import commands


class LaR(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.LaR")
        self.config: Config | None = client.get_cog("Config")
        self.logger.debug("registered.")
        self.mod_mode: ModMode | None = self.client.get_cog("ModMode")

    async def learn(self, message: discord.Message):
        if (
            message.author.id in self.config.config["optout"]
            or message.author.id in self.config.config["blacklist"]
        ):
            return

        if message.reference:
            try:
                reply: discord.Message = await message.channel.fetch_message(
                    message.reference.message_id
                )
            except discord.NotFound:
                return

            if reply.author.id in self.config.config["optout"]:
                return

            content = qna.classes.sanitize_question(
                qna.helpers.get_message_as_string(reply)
            )
            if content + str(message.guild.id) not in self.config.question_map.keys():
                self.config.question_map.update(
                    {
                        content
                        + str(message.guild.id): qna.classes.Question(
                            content,
                            reply.guild.id,
                            reply.channel.id,
                            reply.id,
                            reply.author.id,
                        )
                    }
                )
            response_content = qna.helpers.get_message_as_string(message)
            self.config.question_map[content + str(message.guild.id)].add_response(
                qna.classes.Response(
                    response_content,
                    message.guild.id,
                    message.channel.id,
                    message.id,
                    message.author.id,
                )
            )
            self.logger.debug(
                f"save: {qna.helpers.get_message_as_string(reply)} -> "
                f"{qna.helpers.get_message_as_string(message)}"
            )

    async def reply(self, message: discord.Message):
        guild: discord.Guild = message.guild
        channel: discord.TextChannel = message.channel

        if str(guild.id) in self.config.config["guilds"].keys():
            if channel.id == self.config.config["guilds"][str(guild.id)]["channel"]:
                content = qna.classes.sanitize_question(
                    qna.helpers.get_message_as_string(message)
                )
                placeholder = "I don't know what to say (give me some time to learn)"
                text = placeholder
                server_questions = [
                    q
                    for q in self.config.question_map.values()
                    if q.guild == message.guild.id
                ]
                question = None
                response = None
                if len(server_questions):
                    question = qna.helpers.get_closest_question(
                        server_questions, content
                    )
                    response = qna.helpers.pick_response(question)
                    text = response.text or placeholder
                if message.content.startswith(self.client.command_prefix):
                    text += (
                        "\n(psst, i don't listen to commands here! if you want to run a command, "
                        "go to another channel or use slash commands.)"
                    )
                view = None
                if self.mod_mode.is_in_mod_mode(guild, message.author):
                    view = DeleteView(self.mod_mode, self.config)
                message_reply = await message.reply(text, view=view)
                if self.mod_mode.is_in_mod_mode(guild, message.author):
                    self.mod_mode.save_info(
                        guild, message.author, message_reply, question, response
                    )
                self.logger.debug(
                    f"reply: {qna.helpers.get_message_as_string(message)} -> {text}"
                )
                self.config.messages_sent += 1

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.is_system() or message.guild is None:
            return

        await self.learn(message)
        await self.reply(message)


async def setup(client: commands.Bot):
    await client.add_cog(LaR(client))
