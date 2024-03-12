import os
import json
import logging
from bob import db

logger = logging.getLogger("migration")


def needs_migration():
    return os.path.exists("data.json")


async def start_migration():
    logger.info("loading config file...")
    with open("config.json") as file:
        config = json.load(file)
    logger.info("loading data file...")
    with open("data.json") as file:
        data = file.read()

    logger.info("migrating configuration data...")
    await db.Guild.bulk_create(
        [
            db.Guild(guildId=int(guild), channelId=int(obj["channel"]))
            for guild, obj in config["guilds"].items()
        ]
    )
    await db.Blacklist.bulk_create(
        [
            db.Blacklist(userId=int(user), reason="Migrated from pre-3.0 data.")
            for user in config["blacklist"]
        ]
    )
    await db.OptOutEntry.bulk_create(
        [db.OptOutEntry(userId=int(user)) for user in config["optout"]]
    )

    from bob.qna.json import json_to_questions

    logger.info("migrating qna data (this will take a while)...")
    questions = json_to_questions(data)

    for question in questions:
        dbQuestion = await db.Question.create(
            text=question.text,
            guild=question.guild,
            channel=question.channel,
            message=question.message,
            author=question.author,
        )
        await db.Response.bulk_create(
            [
                db.Response(
                    text=resp.text,
                    count=resp.count,
                    message=resp.message,
                    author=resp.author,
                    question=dbQuestion,
                )
                for resp in question.responses
            ]
        )

    logger.info("cleaning up, we're done")
    os.remove("config.json")
    os.remove("data.json")
    os.remove(".key")
