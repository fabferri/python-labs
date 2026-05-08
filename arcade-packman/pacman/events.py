# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: World update event payload definitions.

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class WorldEvents:
    sounds: list[str] = field(default_factory=list)
    high_score_changed: bool = False
    request_reset_positions: bool = False
    request_load_current_level: bool = False

