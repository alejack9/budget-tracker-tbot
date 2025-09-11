import os
from typing import List


CATEGORIES: List[str] = [
    "food",
    "gifts",
    "health",
    "home",
    "transportation",
    "personal",
    "utilities",
    "travel",
    "debt",
    "other",
    "family",
    "wardrobe",
    "investments",
]

TYPES: List[str] = ["need", "want", "goal"]

UNDO_GRACE_SECONDS = int(os.environ.get("UNDO_GRACE_SECONDS", "10"))