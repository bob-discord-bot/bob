import discord
import logging
from tortoise import Tortoise
from discord.ext import commands
from .db.config import TORTOISE_ORM
from .migration import start_migration, needs_migration


class BobClient(commands.Bot):
    def __init__(self, *, intents: discord.Intents, command_prefix="ba."):
        super().__init__(
            intents=intents, command_prefix=command_prefix, help_command=None
        )
        self.logger = logging.getLogger(self.__class__.__qualname__)

    async def setup_hook(self):
        self.logger.info("Intialising database...")
        await Tortoise.init(config=TORTOISE_ORM)
        if needs_migration():
            self.logger.info("Detected pre-3.0 data, starting migration process...")
            await start_migration()
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
            await self.load_extension(cog)

    async def close(self):
        self.logger.info("Closing database connections...")
        await Tortoise.close_connections()
        await super().close()
