import time
import bob
from bob.db import Guild, Question, Response
import bob.qna as qna
import discord
import logging
import datetime
from discord.ext import commands
from tortoise.expressions import Subquery


class UserCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.UserCommands")
        self.logger.debug("registered.")
        self.to_wipe = {}

    @commands.hybrid_command(brief="Need help? Join the support server!")
    async def support(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Here you go!",
            description=f"You can join [the support server by clicking here](https://discord.gg/uuqZYPYrMj).",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now(),
        )
        embed.set_footer(
            text=bob.get_footer(), icon_url=self.client.user.display_avatar.url
        )

        await ctx.reply(embed=embed)

    @commands.hybrid_command(brief="Get debug information for a reply.")
    async def debug(self, ctx: commands.Context, *, prompt: str):
        guild: discord.Guild = ctx.guild
        message: discord.Message = ctx.message

        guildEntry = await Guild.get_or_none(guildId=guild.id)
        if guildEntry:
            content = qna.classes.sanitize_question(prompt)
            placeholder = "I don't know what to say (give me some time to learn)"
            text = placeholder
            question = None
            response = None
            server_questions = await Question.filter(guild=message.guild.id).all()
            if len(server_questions):
                question = qna.helpers.get_closest_question(server_questions, content)
                response = await qna.helpers.pick_response(question)
                text = response.text if response else placeholder
            embed = None
            if response:
                embed = discord.Embed(
                    title="Debug information",
                    color=discord.Color.gold(),
                    timestamp=datetime.datetime.now(),
                )
                embed.add_field(
                    name="I thought you said...",
                    value=question.text or "(empty message)",
                    inline=False,
                )
                embed.add_field(
                    name="Originally said by",
                    value=f"<@{response.author}> in <#{question.channel}>, replying to <@{question.author}>",
                    inline=False,
                )
                embed.add_field(
                    name="Message link",
                    value=f"https://discord.com/channels/{question.guild}/{question.channel}/{response.message}",
                    inline=False,
                )
                embed.set_footer(
                    text=bob.get_footer(), icon_url=self.client.user.display_avatar.url
                )
            await ctx.reply(text, embed=embed)
        else:
            await ctx.reply(
                "I'm not set up in this server, thus I can't give you debug information for replies."
            )

    @commands.hybrid_command(brief="Wipe your data from bob's dataset.")
    async def clean(self, ctx: commands.Context):
        if ctx.author.id not in self.to_wipe:
            await ctx.reply(
                "Are you sure you want to wipe your data from bob? **This action is irreversible.** "
                "If you're sure you want to wipe your data from bob, please run the command again within "
                "30 seconds."
            )
            self.to_wipe[ctx.author.id] = time.time()
            return
        else:
            if self.to_wipe[ctx.author.id] + 30 > time.time():
                msg = await ctx.reply("Wiping your data (this may take a while)...")
                questions_removed = await Question.filter(author=ctx.author.id).delete()
                responses_removed = await Response.filter(author=ctx.author.id).delete()
                await msg.edit(
                    content=f"Done (removed {questions_removed} prompts and {responses_removed} responses)."
                )
                self.logger.debug(
                    f"{ctx.author} wiped their data (q/a: {questions_removed}, {responses_removed})"
                )
            else:
                del self.to_wipe[ctx.author.id]
                await self.clean(ctx)

    @commands.hybrid_command(brief="Check the bot's statistics.")
    async def stats(self, ctx: commands.Context):
        user_questions = await Question.filter(
            guild=ctx.guild.id, author=ctx.author.id
        ).count()
        user_responses = await Response.filter(
            question_id__in=Subquery(Question.filter(guild=ctx.guild.id).values("id")),
            author=ctx.author.id,
        ).count()
        questions_total = await Question.filter(guild=ctx.guild.id).count()
        responses_total = await Response.filter(
            question_id__in=Subquery(Question.filter(guild=ctx.guild.id).values("id"))
        ).count()
        embed = discord.Embed(
            title="Statistics",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now(),
        )
        embed.add_field(name="Server prompts", value=str(questions_total))
        embed.add_field(name="Server responses", value=str(responses_total))
        embed.add_field(name="Servers", value=str(len(self.client.guilds)))
        embed.add_field(name="Your prompts", value=str(user_questions))
        embed.add_field(name="Your responses", value=str(user_responses))
        embed.set_footer(
            text=bob.get_footer(), icon_url=self.client.user.display_avatar.url
        )
        await ctx.reply(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(UserCommands(client))
