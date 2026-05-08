# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Factory helpers for spawns and pellet distribution.

from __future__ import annotations

import random
from collections.abc import Mapping

from .config import CFG
from .entities import Ghost
from .level import LevelData
from .models import DifficultyConfig, PelletType


GHOST_COLORS = (
    (255, 82, 82),
    (82, 255, 255),
    (255, 184, 82),
    (255, 82, 235),
)

DEFAULT_PLAYER_SPAWN = (14, 18)
DEFAULT_GHOST_SPAWNS = ((1, 3), (26, 3), (13, 10), (14, 10))


# Resolve the player's spawn tile, falling back to a safe default.
def get_player_spawn(level: LevelData) -> tuple[int, int]:
    return level.player_spawns[0] if level.player_spawns else DEFAULT_PLAYER_SPAWN


# Resolve ghost spawn tiles, falling back to default formation points.
def get_ghost_spawns(level: LevelData) -> list[tuple[int, int]]:
    return list(level.ghost_spawns or DEFAULT_GHOST_SPAWNS)


# Deterministically split base pellets across rarity buckets for a level.
def split_pellets(
    base_pellets: set[tuple[int, int]],
    pellet_types: Mapping[str, PelletType],
    seed: int,
) -> dict[str, set[tuple[int, int]]]:
    if not base_pellets:
        return {ptype: set() for ptype in pellet_types}

    result: dict[str, set[tuple[int, int]]] = {ptype: set() for ptype in pellet_types}
    remaining = list(base_pellets)
    rng = random.Random(seed)

    non_common_types = [ptype for ptype in pellet_types.keys() if ptype != "common"]
    for ptype in reversed(non_common_types):
        count = max(1, int(len(base_pellets) * pellet_types[ptype].ratio))
        count = min(count, len(remaining))
        if count > 0:
            selected = rng.sample(remaining, count)
            result[ptype] = set(selected)
            remaining = [pellet for pellet in remaining if pellet not in selected]

    result["common"] = set(remaining)
    return result


# Build ghost entities for the current level and selected difficulty.
def build_ghosts(
    level: LevelData,
    level_index: int,
    difficulty: DifficultyConfig,
) -> list[Ghost]:
    spawns = get_ghost_spawns(level)
    speed = (CFG.ghost_speed + (level_index * 8)) * difficulty.ghost_speed_multiplier
    return [
        Ghost(
            spawn,
            CFG.tile_size,
            speed,
            color,
            sprite_index=i,
            chase_bias=difficulty.ghost_chase_bias,
        )
        for i, (spawn, color) in enumerate(zip(spawns, GHOST_COLORS))
    ]

