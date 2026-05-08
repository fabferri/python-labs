# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Tests for high score storage behavior.

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pacman import storage


class TestStorageModule(unittest.TestCase):
    # Validate High Score Save And Load behavior.
    def test_high_score_save_and_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_file = Path(tmp) / "highscore.json"
            original = storage.HIGHSCORE_FILE
            storage.HIGHSCORE_FILE = tmp_file
            try:
                self.assertEqual(storage.load_high_score(), 0)
                storage.save_high_score(123)
                self.assertEqual(storage.load_high_score(), 123)

                storage.save_high_score(-10)
                self.assertEqual(storage.load_high_score(), 0)
            finally:
                storage.HIGHSCORE_FILE = original


if __name__ == "__main__":
    unittest.main()

