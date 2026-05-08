# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Mutable game state container and transitions.

from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from .entities import Ghost, Player
from .level import LevelData


@dataclass
class GameState:
    level_count: int
    level: LevelData
    player: Player
    player_spawn: tuple[int, int]

    ghosts: list[Ghost] = field(default_factory=list)
    pellets: dict[str, set[tuple[int, int]]] = field(default_factory=dict)

    score: int = 0
    high_score: int = 0
    lives: int = 3

    level_index: int = 0
    game_state: str = "menu"
    game_over: bool = False
    campaign_win: bool = False
    selected_difficulty: int = 1
    selected_theme: int = 0

    dt: float = 0.0
    elapsed_time: float = 0.0
    player_facing: pygame.math.Vector2 = field(default_factory=lambda: pygame.math.Vector2(1, 0))


# Resolve next state after clearing the current level.
def resolve_level_completion(level_index: int, level_count: int) -> tuple[int, str, bool]:
    """Return next level index and game state after clearing current pellets."""
    next_index = level_index + 1
    if next_index < level_count:
        return next_index, "playing", False
    return level_index, "campaign_win", True
