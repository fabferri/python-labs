# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Tests for pure gameplay systems.

from __future__ import annotations

import unittest

import pygame

from pacman.config import PELLET_TYPES
from pacman.entities import Ghost, Player
from pacman.level import get_level_count, load_level
from pacman.state import GameState
from pacman.systems import all_pellets_cleared, consume_pellet_at_player, has_player_ghost_collision


# Helper: Build State.
def _build_state() -> GameState:
    level = load_level(0)
    player_spawn = level.player_spawns[0] if level.player_spawns else (14, 18)
    player = Player(player_spawn, tile_size=24, speed=120.0)
    return GameState(
        level_count=get_level_count(),
        level=level,
        player=player,
        player_spawn=player_spawn,
        pellets={name: set() for name in PELLET_TYPES},
    )


class TestSystemsModule(unittest.TestCase):
    # Validate Consume Pellet Updates Score And Sound Type behavior.
    def test_consume_pellet_updates_score_and_sound_type(self) -> None:
        state = _build_state()
        state.player.position = pygame.math.Vector2((1 + 0.5) * 24, (1 + 0.5) * 24)
        state.pellets["rare"].add((1, 1))

        eaten, sound = consume_pellet_at_player(state, PELLET_TYPES)

        self.assertTrue(eaten)
        self.assertEqual(sound, "rare")
        self.assertEqual(state.score, PELLET_TYPES["rare"].score)

    # Validate All Pellets Cleared Detects Empty State behavior.
    def test_all_pellets_cleared_detects_empty_state(self) -> None:
        state = _build_state()
        self.assertTrue(all_pellets_cleared(state))

        state.pellets["common"].add((1, 1))
        self.assertFalse(all_pellets_cleared(state))

    # Validate Player Ghost Collision Detection behavior.
    def test_player_ghost_collision_detection(self) -> None:
        state = _build_state()
        ghost = Ghost((1, 1), tile_size=24, speed=95.0, color=(255, 0, 0))
        ghost.position = state.player.position.copy()
        state.ghosts = [ghost]

        self.assertTrue(has_player_ghost_collision(state))


if __name__ == "__main__":
    unittest.main()


