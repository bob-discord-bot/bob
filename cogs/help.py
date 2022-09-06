import bob
import discord
import logging
import datetime
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.Help")
        self.logger.debug("registered.")

    @commands.command(brief="Lists commands and information about them.")
    async def help(self, ctx: commands.Context, requested_command: str = None):
        if requested_command:
            target_command = None
            for command in self.client.commands:
                if command.name == requested_command:
                    target_command = command

            if not target_command:
                raise commands.BadArgument(message="Command couldn't be found.")
            else:
                embed = discord.Embed(
                    title=f"bob help | {self.client.command_prefix}{target_command.name}",
                    description=target_command.description or target_command.brief,
                    color=discord.Color.blue(),
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(
                    name="usage",
                    value=target_command.usage or f"{self.client.command_prefix}{target_command.name} "
                                                  f"{target_command.signature}"
                )
                embed.set_footer(text=bob.get_footer(), icon_url=self.client.user.display_avatar.url)

                await ctx.reply(embed=embed)
            return

        embed = discord.Embed(title="bob help", color=discord.Color.blue(), timestamp=datetime.datetime.now())
        for command in sorted(self.client.commands, key=lambda c: c.name):
            command: commands.Command
            if command.hidden:
                continue

            try:
                if not await command.can_run(ctx):
                    continue
            except commands.CommandError:
                continue

            embed.add_field(
                name=self.client.command_prefix + command.name,
                value=command.brief or "No description.",
                inline=False
            )
        embed.set_footer(text=bob.get_footer(), icon_url=self.client.user.display_avatar.url)

        await ctx.reply(embed=embed)


async def setup(client: commands.Bot):
    await client.add_cog(Help(client))
