# LaR: Learn and Reply
import bob.qna as qna
import discord
import logging
from bob.cogs.modmode import DeleteView, ModMode
from bob.db import OptOutEntry, Blacklist, Guild, Question, Response
from discord.ext import commands


class LaR(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.LaR")
        self.logger.debug("registered.")
        self.mod_mode: ModMode | None = self.client.get_cog("ModMode")

    async def learn(self, message: discord.Message):
        if await OptOutEntry.exists(userId=message.author.id) or await Blacklist.exists(
            userId=message.author.id
        ):
            return

        if message.reference:
            try:
                reply: discord.Message = await message.channel.fetch_message(
                    message.reference.message_id
                )
            except discord.NotFound:
                return

            if await OptOutEntry.exists(userId=reply.author.id):
                return

            content = qna.classes.sanitize_question(
                qna.helpers.get_message_as_string(reply)
            )

            question = await Question.get_or_none(guild=message.guild.id, text=content)
            if not question:
                question = await Question.create(
                    text=content,
                    guild=message.guild.id,
                    channel=message.channel.id,
                    message=message.id,
                    author=message.author.id,
                )
            response_content = qna.helpers.get_message_as_string(message)
            response = await Response.get_or_none(
                question=question, text=response_content
            )
            if not response:
                response = await Response.create(
                    text=response_content,
                    question=question,
                    guild=message.guild.id,
                    channel=message.channel.id,
                    message=message.id,
                    author=message.author.id,
                )
            else:
                response.count += 1
                await response.save()
            self.logger.debug(
                f"save: {qna.helpers.get_message_as_string(reply)} -> "
                f"{qna.helpers.get_message_as_string(message)}"
            )

    async def reply(self, message: discord.Message):
        guild: discord.Guild = message.guild
        channel: discord.TextChannel = message.channel

        guildEntry = await Guild.get_or_none(guildId=guild.id)
        if guildEntry:
            if channel.id == guildEntry.channelId:
                content = qna.classes.sanitize_question(
                    qna.helpers.get_message_as_string(message)
                )
                placeholder = "I don't know what to say (give me some time to learn)"
                text = placeholder
                server_questions = await Question.filter(guild=message.guild.id).all()
                question = None
                response = None
                if len(server_questions):
                    question = qna.helpers.get_closest_question(
                        server_questions, content
                    )
                    response = await qna.helpers.pick_response(question)
                    text = response.text or placeholder
                if message.content.startswith(self.client.command_prefix):
                    text += (
                        "\n(psst, i don't listen to commands here! if you want to run a command, "
                        "go to another channel or use slash commands.)"
                    )
                view = None
                # if self.mod_mode.is_in_mod_mode(guild, message.author):
                #     view = DeleteView(self.mod_mode, self.config)
                message_reply = await message.reply(text, view=view)
                # if self.mod_mode.is_in_mod_mode(guild, message.author):
                #     self.mod_mode.save_info(
                #         guild, message.author, message_reply, question, response
                #     )
                self.logger.debug(
                    f"reply: {qna.helpers.get_message_as_string(message)} -> {text}"
                )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.is_system() or message.guild is None:
            return

        await self.learn(message)
        await self.reply(message)


async def setup(client: commands.Bot):
    await client.add_cog(LaR(client))
