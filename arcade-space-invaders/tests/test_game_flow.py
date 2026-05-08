import os
import unittest
from unittest.mock import patch

import pygame

from invaders.game import Game


class _FakeKeys:
    def __init__(self, pressed: set[int] | None = None) -> None:
        self._pressed = pressed or set()

    def __getitem__(self, key: int) -> bool:
        return key in self._pressed


class GameFlowSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        pygame.init()

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def test_wave_advances_after_clearing_aliens(self) -> None:
        game = Game()
        initial_wave = game.state.wave

        for alien in game.state.aliens:
            alien.alive = False

        game._update_world(0.8)

        self.assertEqual(game.state.wave, initial_wave + 1)
        self.assertGreater(len(game.state.aliens), 0)
        self.assertTrue(any(alien.alive for alien in game.state.aliens))

    def test_game_over_restart_resets_core_state_on_r(self) -> None:
        game = Game()
        game.state.show_intro = False
        game.state.score = 1234
        game.state.wave = 4
        game.state.lives = 0
        game.state.game_over = True

        with patch("pygame.key.get_pressed", return_value=_FakeKeys({pygame.K_r})):
            game._update(0.016)

        self.assertEqual(game.state.score, 0)
        self.assertEqual(game.state.wave, 1)
        self.assertEqual(game.state.lives, 3)
        self.assertFalse(game.state.game_over)

    def test_mystery_ship_spawns_when_timer_expires(self) -> None:
        game = Game()
        game.state.mystery_ship = None
        game.state.mystery_spawn_timer = 0.0

        game._update_world(0.016)

        self.assertIsNotNone(game.state.mystery_ship)
        self.assertGreaterEqual(game.state.mystery_spawn_timer, 10.0)
        self.assertLessEqual(game.state.mystery_spawn_timer, 18.0)


if __name__ == "__main__":
    unittest.main()
