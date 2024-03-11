TORTOISE_ORM = {
    "connections": {"default": "sqlite://bob.db"},
    "apps": {
        "bob": {
            "models": ["bob.db", "aerich.models"],
            "default_connection": "default",
        },
    },
}
