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

    @commands.command(brief="lists commands and info about them")
    async def help(self, ctx: commands.Context, requested_command: str = None):
        if requested_command:
            target_command = None
            for command in self.client.commands:
                if command.name == requested_command:
                    target_command = command

            if not target_command:
                raise commands.BadArgument(message="command couldn't be found.")
            else:
                embed = discord.Embed(
                    title=f"bob help | {self.client.command_prefix}{target_command.name}",
                    description=target_command.description or target_command.brief,
                    color=bob.blue_color,
                    timestamp=datetime.datetime.now()
                )
                embed.add_field(
                    name="usage",
                    value=target_command.usage or f"{self.client.command_prefix}{target_command.name} "
                                                  f"{target_command.signature}"
                )
                embed.set_footer(text=f"bob v{bob.__version__}", icon_url=self.client.user.avatar_url)

                await ctx.reply(embed=embed)
            return

        embed = discord.Embed(title="bob help", color=bob.blue_color, timestamp=datetime.datetime.now())
        for command in sorted(self.client.commands, key=lambda c: c.name):
            if command.hidden:
                continue

            try:
                can_run = await command.can_run(ctx)
            except commands.CommandError:
                can_run = False

            if can_run:
                embed.add_field(
                    name=self.client.command_prefix + command.name,
                    value=command.brief or "no description.",
                    inline=False
                )
        embed.set_footer(text=f"bob v{bob.__version__}", icon_url=self.client.user.avatar_url)

        await ctx.reply(embed=embed)


def setup(client: commands.Bot):
    client.add_cog(Help(client))
