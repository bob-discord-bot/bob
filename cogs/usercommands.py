import time

import bob
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
        self.config: Config = client.get_cog('Config')
        self.to_wipe = {}

    @commands.command(brief="Need help? Join the support server!")
    async def support(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Here you go!",
            description=f"You can join [the support server by clicking here](https://discord.gg/uuqZYPYrMj).",
            color=bob.blue_color,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"bob v{bob.__version__}", icon_url=self.client.user.display_avatar.url)

        await ctx.reply(embed=embed)

    @commands.command(brief="Wipe your data from bob's dataset.")
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


async def setup(client: commands.Bot):
    await client.add_cog(UserCommands(client))
