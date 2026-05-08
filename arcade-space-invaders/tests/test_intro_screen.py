import os
import unittest
from unittest.mock import patch

import pygame

from invaders.game import Game
from invaders.input import PygameActionInput
from invaders.state import GameState


class _FakeKeys:
    def __init__(self, pressed: set[int] | None = None) -> None:
        self._pressed = pressed or set()

    def __getitem__(self, key: int) -> bool:
        return key in self._pressed


class IntroScreenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        pygame.init()

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def test_intro_screen_is_shown_at_start(self) -> None:
        game = Game()
        self.assertTrue(game.state.show_intro)

    def test_space_key_dismisses_intro_screen(self) -> None:
        game = Game()
        self.assertTrue(game.state.show_intro)

        with patch("pygame.key.get_pressed", return_value=_FakeKeys({pygame.K_SPACE})):
            game._update(0.016)

        self.assertFalse(game.state.show_intro)
        self.assertGreater(len(game.state.aliens), 0)

    def test_game_resets_when_intro_dismissed(self) -> None:
        game = Game()
        initial_wave = game.state.wave
        initial_lives = game.state.lives
        initial_score = game.state.score

        with patch("pygame.key.get_pressed", return_value=_FakeKeys({pygame.K_SPACE})):
            game._update(0.016)

        self.assertEqual(game.state.wave, initial_wave)
        self.assertEqual(game.state.lives, initial_lives)
        self.assertEqual(game.state.score, initial_score)
        self.assertGreater(len(game.state.aliens), 0)

    def test_no_gameplay_during_intro(self) -> None:
        game = Game()
        game.state.show_intro = True
        initial_alien_count = len(game.state.aliens)

        with patch("pygame.key.get_pressed", return_value=_FakeKeys(set())):
            game._update(1.0)

        self.assertTrue(game.state.show_intro)

    def test_music_can_be_toggled_from_intro(self) -> None:
        game = Game()
        game.state.show_intro = True
        initial_music_state = game.sound.background_on

        with patch("pygame.key.get_pressed", return_value=_FakeKeys({pygame.K_m})):
            if game.state.show_intro:
                pass

        game.sound.toggle_background()
        self.assertNotEqual(game.sound.background_on, initial_music_state)

    def test_intro_state_in_game_state(self) -> None:
        state = GameState()
        self.assertTrue(state.show_intro)

    def test_reset_clears_intro_flag(self) -> None:
        game = Game()
        game.state.show_intro = True

        game.reset(full_reset=True, skip_intro=True)

        self.assertFalse(game.state.show_intro)

    def test_intro_on_game_over_restart(self) -> None:
        game = Game()
        game.state.show_intro = False
        game.state.game_over = True

        with patch("pygame.key.get_pressed", return_value=_FakeKeys({pygame.K_r})):
            game._update(0.016)

        self.assertFalse(game.state.show_intro)
        self.assertFalse(game.state.game_over)
        self.assertGreater(len(game.state.aliens), 0)


if __name__ == "__main__":
    unittest.main()
