import discord
import logging
from tortoise import Tortoise
from discord.ext import commands
from .db.config import TORTOISE_ORM


class BobClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents, command_prefix="ba."):
        super().__init__(
            intents=intents, command_prefix=command_prefix, help_command=None
        )
        self.logger = logging.Logger(self.__class__.__qualname__)

    async def setup_hook(self):
        self.logger.info("Intialising database...")
        await Tortoise.init(config=TORTOISE_ORM)
        for cog in [
            "bob.cogs.modmode",
            "bob.cogs.lar",
            "bob.cogs.configuration",
            "bob.cogs.optin",
            "bob.cogs.usercommands",
            "bob.cogs.help",
            "bob.cogs.status",
            # "bob.cogs.webapi",
            "jishaku",
        ]:
            self.logger.debug(f"loading cog {cog}")
            await self.load_extension(cog)

    async def close(self):
        self.logger.info("Closing database connections...")
        await Tortoise.close_connections()
        await super().close()
