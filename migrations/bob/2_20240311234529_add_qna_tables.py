from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "question" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "text" TEXT NOT NULL,
    "guild" BIGINT NOT NULL,
    "channel" BIGINT NOT NULL,
    "message" BIGINT NOT NULL,
    "author" BIGINT NOT NULL
);
        CREATE TABLE IF NOT EXISTS "response" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "text" TEXT NOT NULL,
    "count" INT NOT NULL  DEFAULT 1,
    "message" BIGINT NOT NULL,
    "author" BIGINT NOT NULL,
    "question_id" INT NOT NULL REFERENCES "question" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "question";
        DROP TABLE IF EXISTS "response";"""
