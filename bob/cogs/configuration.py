import typing

import discord
import logging
from ..db.guild import Guild
from discord.ext import commands


class Configuration(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.Configuration")
        self.logger.debug("registered.")

    @commands.has_permissions(manage_channels=True)
    @commands.hybrid_command(brief="Sets the channel that bob will talk in.")
    async def channel(self, ctx: commands.Context, channel: discord.TextChannel):
        self.logger.debug(f"setting guild {ctx.guild.id}'s channel to {channel.id}")
        guild = await Guild.get_or_none(guildId=ctx.guild.id)
        if guild is None:
            guild = await Guild.create(guildId=ctx.guild.id, channelId=channel.id)
        else:
            guild.channelId = channel.id
            await guild.save()
        await ctx.reply(f"Bob will now talk in {channel.mention}.")


async def setup(client: commands.Bot):
    await client.add_cog(Configuration(client))
