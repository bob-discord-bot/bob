import typing

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
        self.reset_channel_topics.start()

    @commands.has_permissions(manage_channels=True)
    @commands.command(brief="Sets the channel that bob will talk in.")
    async def channel(self, ctx: commands.Context, target_channel: discord.TextChannel):
        self.logger.debug(f"setting guild {ctx.guild.id}'s channel to {target_channel.id}")
        if str(ctx.guild.id) not in self.config.config["guilds"].keys():
            self.config.config["guilds"].update({str(ctx.guild.id): {"channel": target_channel.id}})
        else:
            self.config.config["guilds"][str(ctx.guild.id)]["channel"] = target_channel.id

        await self.update_channel_topic(self.client.get_channel(target_channel.id))
        await ctx.reply(f"Bob will now talk in {target_channel.mention}.")

    async def update_channel_topic(self, channel: discord.TextChannel):
        try:
            await channel.edit(topic=f"talk to bob! | "
                                     f"run **{self.client.command_prefix}help** in an another channel!")
        except discord.Forbidden:
            self.logger.debug(f"I don't have permissions to update {channel}.")

    @tasks.loop(hours=1)
    async def reset_channel_topics(self):
        for guild_id, data in self.config.config["guilds"].items():
            if "channel" in data.keys():
                channel = self.client.get_channel(int(data["channel"]))
                if channel is not None:
                    await self.update_channel_topic(channel)


async def setup(client: commands.Bot):
    await client.add_cog(Configuration(client))
