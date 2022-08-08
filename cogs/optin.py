import logging
from cogs.config import Config
from discord.ext import commands


def blacklist_check(ctx: commands.Context):
    return ctx.author.id not in ctx.cog.config.config["blacklist"]


def optin_check(ctx: commands.Context):
    return ctx.author.id in ctx.cog.config.config["optin"]


def optout_check(ctx: commands.Context):
    return not optin_check(ctx)


class OptIn(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.OptIn")
        self.config: Config = client.get_cog("Config")
        self.logger.debug("registered.")

    @commands.check(blacklist_check)
    @commands.check(optin_check)
    @commands.command(brief="opt-out of bob message collection")
    async def optout(self, ctx: commands.Context):
        if ctx.author.id not in self.config.config["optin"]:
            return await ctx.reply("you're already opted out!")

        self.config.config["optin"].remove(ctx.author.id)
        await ctx.reply("you're now opted out of bob's message collection.")

    @commands.check(blacklist_check)
    @commands.check(optout_check)
    @commands.command(brief="opt-in to bob message collection")
    async def optin(self, ctx: commands.Context):
        if ctx.author.id in self.config.config["optin"]:
            return await ctx.reply("you're already opted in!")

        self.config.config["optin"].append(ctx.author.id)
        await ctx.reply("you're now opted into bob's message collection.\n"
                        "by opting in, you agree to bob's privacy policy. run `b.privacy` for more info.")


async def setup(client: commands.Bot):
    await client.add_cog(OptIn(client))
