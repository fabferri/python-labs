# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Pure deterministic gameplay systems.

from __future__ import annotations

from collections.abc import Mapping

from .models import PelletType
from .state import GameState


# Advance player and ghost actors for one frame.
def advance_actors(state: GameState) -> None:
    state.player.update(state.dt, state.level.walls, state.level.width, state.level.tunnel_rows)
    if state.player.direction.length_squared() > 0:
        state.player_facing = state.player.direction

    for ghost in state.ghosts:
        ghost.update(state.dt, state.level.walls, state.player.tile, state.level.width, state.level.tunnel_rows)


# Consume any pellet at the player position and update score.
def consume_pellet_at_player(state: GameState, pellet_types: Mapping[str, PelletType]) -> tuple[bool, str | None]:
    tile = state.player.tile
    for pellet_type, pellet_set in state.pellets.items():
        if tile not in pellet_set:
            continue

        pellet_set.remove(tile)
        state.score += pellet_types[pellet_type].score
        sound_key = "rare" if pellet_type in ("rare", "treasure", "super", "crystal") else "pellet"
        return True, sound_key

    return False, None


# Return whether all pellet buckets are empty.
def all_pellets_cleared(state: GameState) -> bool:
    return all(not values for values in state.pellets.values())


# Return whether player currently collides with any ghost.
def has_player_ghost_collision(state: GameState) -> bool:
    for ghost in state.ghosts:
        if state.player.position.distance_to(ghost.position) < (state.player.radius + ghost.radius - 3):
            return True
    return False

