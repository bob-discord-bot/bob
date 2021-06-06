import discord
import logging
from cogs.config import Config
from discord.ext import commands


class Configuration(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.Configuration")
        self.config: Config = client.get_cog("Config")
        self.logger.debug("registered.")

    @commands.has_permissions(manage_channels=True)
    @commands.command(brief="sets the channel bob should talk in")
    async def channel(self, ctx: commands.Context, target_channel: discord.TextChannel):
        self.logger.debug(f"setting guild {ctx.guild.id}'s channel to {target_channel.id}")
        if str(ctx.guild.id) not in self.config.config["guilds"].keys():
            self.config.config["guilds"].update({str(ctx.guild.id): {"channel": target_channel.id}})
        else:
            self.config.config["guilds"][str(ctx.guild.id)]["channel"] = target_channel.id

        await ctx.reply(f"done! bob will now talk in {target_channel.mention}.")


def setup(client: commands.Bot):
    client.add_cog(Configuration(client))
