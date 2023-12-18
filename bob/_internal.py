import json
from bob import qna


def __save_data_impl(logger, config, question_map):
    logger.debug("saving data...")

    with open("config.json", "w+") as file:
        json.dump(config, file)

    with open("data.json", "w+") as file:
        file.write(qna.json.questions_to_json(list(question_map.values())))

    logger.debug("done saving data.")


# wtf???
_Config__save_data_impl = __save_data_impl
