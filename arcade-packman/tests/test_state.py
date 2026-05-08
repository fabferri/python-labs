# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Tests for level completion state transitions.

from __future__ import annotations

import unittest

from pacman.state import resolve_level_completion


class TestStateTransitions(unittest.TestCase):
    # Validate Level Completion Advances When More Levels Exist behavior.
    def test_level_completion_advances_when_more_levels_exist(self) -> None:
        next_index, game_state, campaign_win = resolve_level_completion(level_index=0, level_count=3)
        self.assertEqual(next_index, 1)
        self.assertEqual(game_state, "playing")
        self.assertFalse(campaign_win)

    # Validate Level Completion Wins On Last Level behavior.
    def test_level_completion_wins_on_last_level(self) -> None:
        next_index, game_state, campaign_win = resolve_level_completion(level_index=2, level_count=3)
        self.assertEqual(next_index, 2)
        self.assertEqual(game_state, "campaign_win")
        self.assertTrue(campaign_win)


if __name__ == "__main__":
    unittest.main()

