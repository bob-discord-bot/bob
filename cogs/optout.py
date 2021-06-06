import bob
import logging
from discord.ext import commands


class OptOut(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.OptOut")
        self.logger.debug("registered.")

    @commands.command(brief="opt-out of bob message collection (opted in by default)")
    async def optout(self, ctx: commands.Context):
        if ctx.author.id in bob.config["optout"]:
            return await ctx.reply("you're already opted out!")

        bob.config["optout"].append(ctx.author.id)
        await ctx.reply("you're now opted out of bob's message collection.\nbob will not use your messages to learn.")

    @commands.command(brief="opt-in to bob message collection")
    async def optin(self, ctx: commands.Context):
        if ctx.author.id not in bob.config["optout"]:
            return await ctx.reply("you're already opted in!")

        bob.config["optout"].remove(ctx.author.id)
        await ctx.reply("you're now opted into bob's message collection.")


def setup(client: commands.Bot):
    client.add_cog(OptOut(client))
