# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Tests for deterministic pellet distribution behavior.

from __future__ import annotations

import unittest

from pacman.config import PELLET_TYPES
from pacman.factories import split_pellets


class TestFactoriesModule(unittest.TestCase):
    # Validate Split Pellets Is Deterministic And Lossless behavior.
    def test_split_pellets_is_deterministic_and_lossless(self) -> None:
        pellets = {(x, y) for x in range(1, 8) for y in range(1, 4)}

        first = split_pellets(set(pellets), PELLET_TYPES, seed=777)
        second = split_pellets(set(pellets), PELLET_TYPES, seed=777)

        self.assertEqual(first, second)
        combined: set[tuple[int, int]] = set()
        for values in first.values():
            combined.update(values)
        self.assertEqual(combined, pellets)


if __name__ == "__main__":
    unittest.main()

