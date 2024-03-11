from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "blacklist" (
    "userId" BIGINT NOT NULL  PRIMARY KEY,
    "reason" TEXT
);
        CREATE TABLE IF NOT EXISTS "guild" (
    "guildId" BIGINT NOT NULL  PRIMARY KEY,
    "channelId" BIGINT NOT NULL
);
        CREATE TABLE IF NOT EXISTS "optoutentry" (
    "userId" BIGINT NOT NULL  PRIMARY KEY
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "blacklist";
        DROP TABLE IF EXISTS "guild";
        DROP TABLE IF EXISTS "optoutentry";"""
