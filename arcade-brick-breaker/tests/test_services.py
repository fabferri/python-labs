import unittest

from brickbreaker import config
from brickbreaker.factories import create_initial_state
from brickbreaker.services import EventController, PlayerController


class FakeActionInput:
    def __init__(self, pressed_actions: set[str]) -> None:
        self._pressed_actions = pressed_actions

    def pressed(self, action: str) -> bool:
        return action in self._pressed_actions


class ServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.controller = EventController()
        self.player_controller = PlayerController()

    def test_start_action_from_menu_starts_game(self) -> None:
        state = create_initial_state()

        outcome = self.controller.handle_action(state, "start_launch")

        self.assertEqual("start", outcome)
        self.assertFalse(state.menu_active)
        self.assertTrue(state.started)

    def test_toggle_sfx_action_flips_state(self) -> None:
        state = create_initial_state()
        self.assertTrue(state.sfx_enabled)

        outcome = self.controller.handle_action(state, "toggle_sfx")

        self.assertEqual("sfx-off", outcome)
        self.assertFalse(state.sfx_enabled)

    def test_pause_menu_toggles_pause_when_game_running(self) -> None:
        state = create_initial_state()
        state.menu_active = False

        first = self.controller.handle_action(state, "pause_menu")
        second = self.controller.handle_action(state, "pause_menu")

        self.assertEqual("pause", first)
        self.assertEqual("resume", second)
        self.assertFalse(state.paused)

    def test_pause_menu_returns_to_menu_after_game_over(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.game_over = True
        state.started = True

        outcome = self.controller.handle_action(state, "pause_menu")

        self.assertEqual("menu", outcome)
        self.assertTrue(state.menu_active)
        self.assertFalse(state.started)

    def test_start_launch_advances_from_level_cleared(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.level_cleared = True
        state.level = 1

        outcome = self.controller.handle_action(state, "start_launch")

        self.assertEqual("next-level", outcome)
        self.assertEqual(2, state.level)
        self.assertTrue(state.started)

    def test_player_controller_moves_left_and_clamps_at_screen_edge(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.paddle.rect.left = 0

        self.player_controller.update(state, FakeActionInput({"move_left"}))

        self.assertEqual(0, state.paddle.rect.left)

    def test_player_controller_moves_right_and_clamps_at_screen_edge(self) -> None:
        state = create_initial_state()
        state.menu_active = False
        state.paddle.rect.right = config.SCREEN_WIDTH

        self.player_controller.update(state, FakeActionInput({"move_right"}))

        self.assertEqual(config.SCREEN_WIDTH, state.paddle.rect.right)


if __name__ == "__main__":
    unittest.main()
