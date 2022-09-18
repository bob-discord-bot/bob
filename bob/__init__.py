"""
Constants used by bob.
"""
__version__ = "2.4.0 beta.1"

import random

CATCHPHRASES = [
    "Your conversation partner.",
    "Check us out on Top.gg!",
    "A bit dumb and a bit smart."
]

SEPARATOR = '•'


def get_footer():
    return f"bob v{__version__} {SEPARATOR} {random.choice(CATCHPHRASES)}"
