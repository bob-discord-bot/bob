import json
import os.path

default_config = {
    "scrape_channel": 0,
    "target_channel": 0,
    "debug_channel": 0,
    "scrape_amount": 50000
}

if not os.path.exists("config.json"):
    print("WARNING: Config file not found! Using default config.")
    config = default_config
else:
    with open("config.json") as file:
        config = json.load(file)
