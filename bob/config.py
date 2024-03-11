import yaml

with open(".config.yml") as file:
    _data = yaml.load(file, Loader=yaml.FullLoader)


def get(key: str):
    if key not in _data:
        raise KeyError(
            f"Key {key} does not exist in your `.config.yml`. Did you forget to update it?"
        )
    return _data[key]
