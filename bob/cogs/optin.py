import logging
import typing

from bob.db import OptOutEntry, Blacklist
from discord.ext import commands


async def blacklist_check(ctx: commands.Context):
    return not await Blacklist.exists(userId=ctx.author.id)


class OptIn(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.OptIn")
        self.logger.debug("registered.")

    @commands.check(blacklist_check)
    @commands.hybrid_command(brief="Opt-out of bob message collection.")
    async def optout(self, ctx: commands.Context):
        if await OptOutEntry.exists(userId=ctx.author.id):
            return await ctx.reply("You're already opted out!")

        await OptOutEntry.create(userId=ctx.author.id)
        await ctx.reply(
            "You've opted out of bob's message collection. If you want to remove your message data, "
            f"run **{self.client.command_prefix}clean**."
        )

    @commands.check(blacklist_check)
    @commands.hybrid_command(brief="Opt-in to bob message collection.")
    async def optin(self, ctx: commands.Context):
        if not await OptOutEntry.exists(userId=ctx.author.id):
            return await ctx.reply("You're already opted in.")

        await OptOutEntry.filter(userId=ctx.author.id).delete()
        await ctx.reply(
            "You've opted into bob's message collection.\nRemember that by opting in, "
            "you agree to bob's Terms of Service and Privacy Policy: https://bob.omame.xyz/terms."
        )


async def setup(client: commands.Bot):
    await client.add_cog(OptIn(client))
