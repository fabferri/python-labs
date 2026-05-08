# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Tests for level parsing and structural validity.

from __future__ import annotations

import unittest

from pacman.level import get_level_count, load_level


class TestLevelModule(unittest.TestCase):
    # Validate All Levels Have Valid Data behavior.
    def test_all_levels_have_valid_data(self) -> None:
        total_levels = get_level_count()
        self.assertGreaterEqual(total_levels, 1)

        for idx in range(total_levels):
            level = load_level(idx)
            self.assertGreater(len(level.walls), 0)
            self.assertGreater(len(level.pellets), 0)
            self.assertGreaterEqual(len(level.player_spawns), 1)
            self.assertGreaterEqual(len(level.ghost_spawns), 1)
            self.assertGreater(len(level.tunnel_rows), 0)
            self.assertGreater(level.width, 0)
            self.assertGreater(level.height, 0)


if __name__ == "__main__":
    unittest.main()

