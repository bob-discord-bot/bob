import os
import json
import logging
from bob import db
from tqdm import tqdm

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

    logger.info("migrating qna data (this might take a while)...")
    questions = json_to_questions(data)

    logger.info("migrating questions...")
    await db.Question.bulk_create(
        [
            db.Question(
                id=idx + 1,
                text=q.text,
                guild=q.guild,
                channel=q.channel,
                message=q.message,
                author=q.author,
            )
            for idx, q in enumerate(questions)
        ]
    )

    logger.info("...and responses...")
    await db.Response.bulk_create(
        [
            db.Response(
                question_id=q_idx + 1,
                text=r.text,
                count=r.count,
                message=r.message,
                author=r.author,
            )
            for q_idx, q in enumerate(questions)
            for r in q.responses
        ]
    )

    logger.info("cleaning up, we're done")
    os.remove("config.json")
    os.remove("data.json")
    os.remove(".key")
