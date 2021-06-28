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

    @commands.command(brief="invite me to your server!")
    async def invite(self, ctx: commands.Context):
        embed = discord.Embed(
            title="here you go!",
            description=f"you can invite me to your server by [clicking on this link](https://discord.com/api/oauth2/"
                        f"authorize?client_id={self.client.user.id}&permissions=281616&scope=bot).",
            color=bob.blue_color,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"bob v{bob.__version__}", icon_url=self.client.user.avatar_url)

        await ctx.reply(embed=embed)

    @commands.command(brief="need help? join the support server!")
    async def support(self, ctx: commands.Context):
        embed = discord.Embed(
            title="here you go!",
            description=f"you can join the support server by [clicking on this link](https://discord.gg/uuqZYPYrMj).",
            color=bob.blue_color,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"bob v{bob.__version__}", icon_url=self.client.user.avatar_url)

        await ctx.reply(embed=embed)

    @commands.command(brief="view bob's privacy policy.")
    async def privacy(self, ctx: commands.Context):
        embed = discord.Embed(
            title="privacy policy",
            color=bob.blue_color,
            timestamp=datetime.datetime.now()
        )

        embed.add_field(
            name="1. message collection",
            value="if opted-in, bob will use your messages, including attachments, to learn and expand its database.\n"
                  "bob will additionally log guild, channel, message and author IDs.",
            inline=False
        )
        embed.add_field(
            name="2. message usage",
            value="bob will use the messages in its database to respond to messages from other users.",
            inline=False
        )
        embed.add_field(
            name="3. data protection",
            value="bob will keep sensitive data (such as guild, channel, message and author IDs) private, and will be "
                  "visible only to the bot owner.\n"
                  "bob will never send sensitive data in a reply to a user, unless it is a reply to a message in "
                  "the database.",
            inline=False
        )
        embed.add_field(
            name="4. data removal",
            value="currently you cannot request data removal for your account.\n"
                  "if you had accidentally sent a sensitive message and bob had learned it as a reply, you can contact "
                  "the bot owner privately through the support server to get the reply removed.",
            inline=False
        )
        embed.add_field(
            name="5. blacklisting",
            value="if the bot owner sees bob learn inappropriate messages from your replies, they may remove your "
                  "replies and add you to the blacklist.\nthe blacklist stops bob from learning your replies, but "
                  "it won't stop bob from replying to you.",
            inline=False
        )
        embed.set_footer(text=f"bob v{bob.__version__}", icon_url=self.client.user.avatar_url)

        await ctx.reply(embed=embed)


def setup(client: commands.Bot):
    client.add_cog(UserCommands(client))
