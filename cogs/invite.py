import bob
import discord
import logging
import subprocess
from discord.ext import commands


class Invite(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.Invite")
        self.logger.debug("registered.")

    @commands.command(brief="invite me to your server!")
    async def invite(self, ctx: commands.Context):
        embed = discord.Embed(
            title="here you go!",
            description=f"you can invite me to your server by [clicking on this link](https://discord.com/api/oauth2/"
                        f"authorize?client_id={self.client.user.id}&permissions=3072&scope=bot)",
            color=bob.blue_color
        )
        await ctx.reply(embed=embed)


def setup(client: commands.Bot):
    client.add_cog(Invite(client))
