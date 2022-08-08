import bob
import discord
import logging
import datetime
from discord.ext import commands


class UserCommands(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.UserCommands")
        self.logger.debug("registered.")

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


async def setup(client: commands.Bot):
    await client.add_cog(UserCommands(client))
