# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: High score persistence utilities.

from __future__ import annotations

import json
from pathlib import Path


HIGHSCORE_FILE = Path(__file__).resolve().parent.parent / "highscore.json"


# Load high score from persistent storage.
def load_high_score() -> int:
    if not HIGHSCORE_FILE.exists():
        return 0

    try:
        data = json.loads(HIGHSCORE_FILE.read_text(encoding="utf-8"))
        value = int(data.get("high_score", 0))
        return max(0, value)
    except (ValueError, OSError, json.JSONDecodeError):
        return 0


# Save high score to persistent storage.
def save_high_score(score: int) -> None:
    best = max(0, int(score))
    payload = {"high_score": best}
    HIGHSCORE_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")
