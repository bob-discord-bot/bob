import logging
import typing

from cogs.config import Config
from discord.ext import commands


def blacklist_check(ctx: commands.Context):
    cog: typing.Union[OptIn, None] = ctx.cog
    return ctx.author.id not in cog.config.config["blacklist"]


class OptIn(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.OptIn")
        self.config: typing.Union[Config, None] = client.get_cog("Config")
        self.logger.debug("registered.")

    @commands.check(blacklist_check)
    @commands.command(brief="Opt-out of bob message collection.")
    async def optout(self, ctx: commands.Context):
        if ctx.author.id in self.config.config["optout"]:
            return await ctx.reply("You're already opted out!")

        self.config.config["optout"].append(ctx.author.id)
        await ctx.reply("You've opted out of bob's message collection. If you want to remove your message data, "
                        f"run **{self.client.command_prefix}clean**.")

    @commands.check(blacklist_check)
    @commands.command(brief="Opt-in to bob message collection.")
    async def optin(self, ctx: commands.Context):
        if ctx.author.id not in self.config.config["optout"]:
            return await ctx.reply("You're already opted in. bob is opt-out by default since September 2022.")

        self.config.config["optout"].remove(ctx.author.id)
        await ctx.reply("You've opted into bob's message collection.\nRemember that by opting in, "
                        "you agree to bob's Terms of Service and Privacy Policy: https://bob.omame.xyz/terms.")


async def setup(client: commands.Bot):
    await client.add_cog(OptIn(client))
