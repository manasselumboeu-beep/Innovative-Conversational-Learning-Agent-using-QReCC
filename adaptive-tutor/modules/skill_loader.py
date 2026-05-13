import os
from functools import lru_cache

_BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "skills")


@lru_cache(maxsize=64)
def load_skill(relative_path: str) -> str:
    """Load a SKILL.md file by path relative to the skills/ directory."""
    full_path = os.path.join(_BASE, relative_path)
    if not os.path.exists(full_path):
        return ""
    with open(full_path, encoding="utf-8") as f:
        return f.read()


def load_index() -> str:
    return load_skill("INDEX.md")


def load_explanation_skill(style: str) -> str:
    return load_skill(f"explanation/{style}/SKILL.md")


def load_interaction_skill(name: str) -> str:
    return load_skill(f"interaction/{name}/SKILL.md")


def load_meta_skill(name: str) -> str:
    return load_skill(f"meta/{name}/SKILL.md")
