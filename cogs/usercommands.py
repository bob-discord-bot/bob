import time
import typing

import bob
import qna
import discord
import logging
import datetime
from discord.ext import commands

from cogs.config import Config


class UserCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.UserCommands")
        self.logger.debug("registered.")
        self.config: typing.Union[Config, None] = client.get_cog("Config")
        self.to_wipe = {}

    @commands.hybrid_command(brief="Need help? Join the support server!")
    async def support(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Here you go!",
            description=f"You can join [the support server by clicking here](https://discord.gg/uuqZYPYrMj).",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=bob.get_footer(), icon_url=self.client.user.display_avatar.url)

        await ctx.reply(embed=embed)

    @commands.hybrid_command(brief="Get debug information for a reply.")
    async def debug(self, ctx: commands.Context, *, prompt: str):
        guild: discord.Guild = ctx.guild
        message: discord.Message = ctx.message

        if str(guild.id) in self.config.config["guilds"].keys():
            content = qna.classes.sanitize_question(prompt)
            placeholder = "I don't know what to say (give me some time to learn)"
            text = placeholder
            question = None
            response = None
            server_questions = [q for q in self.config.question_map.values() if q.guild == message.guild.id]
            if len(server_questions):
                question = qna.helpers.get_closest_question(server_questions, content,
                                                            message.guild.id)
                response = qna.helpers.pick_response(question)
                text = response.text or placeholder
            embed = None
            if response:
                embed = discord.Embed(
                    title="Debug information",
                    color=discord.Color.gold(),
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(name="I thought you said...", value=question.text, inline=False)
                embed.add_field(name="Originally said by", value=f"<@{response.author}> in <#{question.channel}>, replying to <@{question.author}>", inline=False)
                embed.add_field(name="Message link", value=f"https://discord.com/channels/{response.guild}/{response.channel}/{response.message}", inline=False)
                embed.set_footer(text=bob.get_footer(), icon_url=self.client.user.display_avatar.url)
            await message.reply(text, embed=embed)
        else:
            await message.reply("I'm not set up in this server, thus I can't give you debug information for replies.")

    @commands.hybrid_command(brief="Wipe your data from bob's dataset.")
    async def clean(self, ctx: commands.Context):
        if ctx.author.id not in self.to_wipe:
            await ctx.reply("Are you sure you want to wipe your data from bob? **This action is irreversible.** "
                            "If you're sure you want to wipe your data from bob, please run the command again within "
                            "30 seconds.")
            self.to_wipe[ctx.author.id] = time.time()
            return
        else:
            if self.to_wipe[ctx.author.id] + 30 > time.time():
                msg = await ctx.reply("Wiping your data (this may take a while)...")
                questions_removed = 0
                responses_removed = 0
                question_map = self.config.question_map.copy()
                for question_key in question_map:
                    question = self.config.question_map[question_key]
                    if question.author == ctx.author.id:
                        self.config.question_map.pop(question_key)
                        questions_removed += 1
                        continue
                    responses = question.responses.copy()
                    for response in responses:
                        if response.author == ctx.author.id:
                            question.responses.remove(response)
                            responses_removed += 1
                await msg.edit(content=f"Done (removed {questions_removed} prompts and {responses_removed} responses).")
                self.logger.debug(f"{ctx.author} wiped their data (q/a: {questions_removed}, {responses_removed})")
            else:
                del self.to_wipe[ctx.author.id]
                await self.clean(ctx)

    @commands.hybrid_command(brief="Check the bot's statistics.")
    async def stats(self, ctx: commands.Context):
        user_questions = 0
        user_responses = 0
        questions_total = 0
        responses_total = 0
        for question_key in self.config.question_map:
            question = self.config.question_map[question_key]
            if question.guild != ctx.guild.id:
                continue
            questions_total += 1
            if question.author == ctx.author.id:
                user_questions += 1
            for response in question.responses:
                if response.author == ctx.author.id:
                    user_responses += 1
            responses_total += len(question.responses)
        embed = discord.Embed(
            title="Statistics",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(
            name="Server prompts",
            value=str(questions_total)
        )
        embed.add_field(
            name="Server responses",
            value=str(responses_total)
        )
        embed.add_field(
            name="Servers",
            value=str(len(self.client.guilds))
        )
        embed.add_field(
            name="Your prompts",
            value=str(user_questions)
        )
        embed.add_field(
            name="Your responses",
            value=str(user_responses)
        )
        embed.set_footer(text=bob.get_footer(), icon_url=self.client.user.display_avatar.url)
        await ctx.reply(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(UserCommands(client))
