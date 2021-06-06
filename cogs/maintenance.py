import bob
import discord
import logging
import subprocess
from discord.ext import commands


class Maintenance(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.Maintenance")
        self.logger.debug("registered.")

    @commands.is_owner()
    @commands.command()
    async def stop(self, ctx: commands.Context):
        await ctx.reply("stopping...")
        await self.client.close()

    @commands.is_owner()
    @commands.command()
    async def update(self, ctx: commands.Context):
        await ctx.reply("updating...")
        subprocess.run(["git", "pull"])

        await ctx.reply("stopping...")
        await self.client.close()

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
    client.add_cog(Maintenance(client))
