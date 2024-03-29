import logging
import discord
from discord.ext import commands
from bob.db import Question, Response


class ModMode(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.logger = logging.getLogger("cogs.ModMode")
        self.logger.debug("registered.")
        self.data = {}

    def is_in_mod_mode(self, guild: discord.Guild, user: discord.Member):
        return f"{guild.id}+{user.id}" in self.data

    def save_info(
        self,
        guild: discord.Guild,
        user: discord.Member,
        message: discord.Message,
        question: Question,
        response: Response,
    ):
        self.data[f"{guild.id}+{user.id}"][message.id] = {
            "question": question,
            "response": response,
        }
        self.logger.debug(
            "[%s] (%i) %s -> %s",
            str(user),
            message.id,
            question.text,
            response.text if response else "whoops! response is None",
        )

    @commands.has_permissions(manage_messages=True)
    @commands.hybrid_command(brief="Toggles moderator mode.")
    async def mod(self, ctx: commands.Context):
        if not self.is_in_mod_mode(ctx.guild, ctx.author):
            self.data[f"{ctx.guild.id}+{ctx.author.id}"] = {}
            await ctx.reply(
                "You have entered **moderator mode**. Whenever bob replies to your messages, "
                "you will be able to delete its replies from the database."
            )
        else:
            del self.data[f"{ctx.guild.id}+{ctx.author.id}"]
            await ctx.reply("You have left moderator mode.")


class DeleteView(discord.ui.View):
    def __init__(self, mod_mode: ModMode):
        super().__init__()
        self.mod_mode = mod_mode

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, _: discord.ui.Button):
        message = interaction.message
        guild = interaction.guild
        user = interaction.user
        if not self.mod_mode.is_in_mod_mode(guild, user):
            return await interaction.response.send_message(
                "You are not in moderator mode.", ephemeral=True
            )
        print(message.id, self.mod_mode.data)
        if message.id in self.mod_mode.data[f"{guild.id}+{user.id}"]:
            question: Question = self.mod_mode.data[f"{guild.id}+{user.id}"][
                message.id
            ]["question"]
            response: Response = self.mod_mode.data[f"{guild.id}+{user.id}"][
                message.id
            ]["response"]
            await response.delete()
            self.mod_mode.logger.debug(
                "Deleted response %s -> %s", question.text, response.text
            )

            if (await question.responses.all().count()) == 0:
                await question.delete()
                self.mod_mode.logger.debug("Deleted question %s", question.text)

            del self.mod_mode.data[f"{guild.id}+{user.id}"][message.id]

            await message.delete()
            await interaction.response.send_message(
                "Deleted this reply from bob's database.", ephemeral=True
            )
        else:
            return await interaction.response.send_message(
                "You're able to delete replies that only you generated.", ephemeral=True
            )


async def setup(client: commands.Bot):
    await client.add_cog(ModMode(client))
