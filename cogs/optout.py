import logging
from cogs.config import Config
from discord.ext import commands


class OptOut(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.OptOut")
        self.config: Config = client.get_cog("Config")
        self.logger.debug("registered.")

    @commands.command(brief="opt-out of bob message collection (opted in by default)")
    async def optout(self, ctx: commands.Context):
        if ctx.author.id in self.config.config["optout"]:
            return await ctx.reply("you're already opted out!")

        self.config.config["optout"].append(ctx.author.id)
        await ctx.reply("you're now opted out of bob's message collection.\nbob will not use your messages to learn.")

    @commands.command(brief="opt-in to bob message collection")
    async def optin(self, ctx: commands.Context):
        if ctx.author.id not in self.config.config["optout"]:
            return await ctx.reply("you're already opted in!")

        self.config.config["optout"].remove(ctx.author.id)
        await ctx.reply("you're now opted into bob's message collection.")


def setup(client: commands.Bot):
    client.add_cog(OptOut(client))
