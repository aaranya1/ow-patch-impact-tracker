"""Load config.toml (falls back to config.example.toml so tests run on a fresh clone)."""

import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_config(path: str | Path | None = None) -> dict:
    if path is None:
        path = ROOT / "config.toml"
        if not path.exists():
            path = ROOT / "config.example.toml"
    with open(path, "rb") as f:
        return tomllib.load(f)
