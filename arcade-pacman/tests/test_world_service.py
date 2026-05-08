# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Tests for world service event behavior.

from __future__ import annotations

import unittest

from pacman.config import PELLET_TYPES
from pacman.entities import Ghost, Player
from pacman.level import get_level_count, load_level
from pacman.state import GameState
from pacman.world_service import WorldUpdater


class TestWorldServiceEvents(unittest.TestCase):
    # Validate World Updater Emits Expected Events On Rare Pellet behavior.
    def test_world_updater_emits_expected_events_on_rare_pellet(self) -> None:
        level = load_level(0)
        player_spawn = level.player_spawns[0] if level.player_spawns else (14, 18)
        player = Player(player_spawn, tile_size=24, speed=120.0)
        state = GameState(
            level_count=get_level_count(),
            level=level,
            player=player,
            player_spawn=player_spawn,
            pellets={name: set() for name in PELLET_TYPES},
            game_state="playing",
        )
        state.pellets["rare"].add(player.tile)

        events = WorldUpdater().update(state, PELLET_TYPES)

        self.assertIn("rare", events.sounds)
        self.assertTrue(events.high_score_changed)

    # Validate World Updater Requests Next Level After Last Pellet behavior.
    def test_world_updater_requests_next_level_after_last_pellet(self) -> None:
        level = load_level(0)
        player_spawn = level.player_spawns[0] if level.player_spawns else (14, 18)
        player = Player(player_spawn, tile_size=24, speed=120.0)
        state = GameState(
            level_count=3,
            level=level,
            player=player,
            player_spawn=player_spawn,
            pellets={name: set() for name in PELLET_TYPES},
            game_state="playing",
            level_index=0,
        )
        state.pellets["common"].add(player.tile)

        events = WorldUpdater().update(state, PELLET_TYPES)

        self.assertTrue(events.request_load_current_level)
        self.assertEqual(state.level_index, 1)
        self.assertEqual(state.game_state, "playing")
        self.assertIn("win", events.sounds)

    # Validate World Updater Sets Game Over On Last Life Collision behavior.
    def test_world_updater_sets_game_over_on_last_life_collision(self) -> None:
        level = load_level(0)
        player_spawn = level.player_spawns[0] if level.player_spawns else (14, 18)
        player = Player(player_spawn, tile_size=24, speed=120.0)
        ghost = Ghost((1, 1), tile_size=24, speed=95.0, color=(255, 0, 0))
        ghost.position = player.position.copy()
        state = GameState(
            level_count=3,
            level=level,
            player=player,
            player_spawn=player_spawn,
            ghosts=[ghost],
            pellets={name: set() for name in PELLET_TYPES},
            game_state="playing",
            lives=1,
            score=100,
            high_score=90,
        )

        events = WorldUpdater().update(state, PELLET_TYPES)

        self.assertEqual(state.lives, 0)
        self.assertEqual(state.game_state, "game_over")
        self.assertTrue(state.game_over)
        self.assertIn("death", events.sounds)
        self.assertTrue(events.high_score_changed)


if __name__ == "__main__":
    unittest.main()

