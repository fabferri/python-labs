# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Tests for session service behavior.

from __future__ import annotations

import unittest

from pacman.config import DIFFICULTIES, PELLET_TYPES
from pacman.entities import Player
from pacman.level import get_level_count, load_level
from pacman.session_service import SessionService
from pacman.state import GameState


class TestSessionService(unittest.TestCase):
    # Validate Current Difficulty Maps Selected Index behavior.
    def test_current_difficulty_maps_selected_index(self) -> None:
        level = load_level(0)
        player_spawn = level.player_spawns[0] if level.player_spawns else (14, 18)
        player = Player(player_spawn, tile_size=24, speed=120.0)
        state = GameState(
            level_count=get_level_count(),
            level=level,
            player=player,
            player_spawn=player_spawn,
            selected_difficulty=2,
            pellets={name: set() for name in PELLET_TYPES},
        )

        difficulty = SessionService().current_difficulty(state)

        self.assertEqual(difficulty, DIFFICULTIES[2])


if __name__ == "__main__":
    unittest.main()

