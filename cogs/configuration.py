﻿import typing

import discord
import logging
from discord.ext import tasks
from cogs.config import Config
from discord.ext import commands


class Configuration(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.Configuration")
        self.config: typing.Union[Config, None] = client.get_cog("Config")
        self.logger.debug("registered.")

    @commands.has_permissions(manage_channels=True)
    @commands.command(brief="Sets the channel that bob will talk in.")
    async def channel(self, ctx: commands.Context, target_channel: discord.TextChannel):
        self.logger.debug(f"setting guild {ctx.guild.id}'s channel to {target_channel.id}")
        if str(ctx.guild.id) not in self.config.config["guilds"].keys():
            self.config.config["guilds"].update({str(ctx.guild.id): {"channel": target_channel.id}})
        else:
            self.config.config["guilds"][str(ctx.guild.id)]["channel"] = target_channel.id
        await ctx.reply(f"Bob will now talk in {target_channel.mention}.")


async def setup(client: commands.Bot):
    await client.add_cog(Configuration(client))
