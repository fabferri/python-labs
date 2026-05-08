import unittest

import pygame

from invaders.input import DEFAULT_ACTION_KEYMAP, PygameActionInput


class _KeyStateFake:
    def __init__(self, pressed_keys: set[int] | None = None) -> None:
        self._pressed = pressed_keys or set()

    def __getitem__(self, key: int) -> bool:
        return key in self._pressed


class InputAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()

    def test_action_for_key_returns_action_name(self) -> None:
        action = PygameActionInput.action_for_key(pygame.K_SPACE)
        self.assertIn(action, ["start_game", "shoot"])

    def test_action_for_key_returns_none_for_unknown_key(self) -> None:
        action = PygameActionInput.action_for_key(pygame.K_F1)
        self.assertIsNone(action)

    def test_action_for_key_with_custom_keymap(self) -> None:
        custom_map = {"custom_action": (pygame.K_x,)}
        action = PygameActionInput.action_for_key(pygame.K_x, keymap=custom_map)
        self.assertEqual(action, "custom_action")

    def test_pressed_returns_true_for_active_key(self) -> None:
        keys = _KeyStateFake({pygame.K_LEFT})
        adapter = PygameActionInput(keys)

        self.assertTrue(adapter.pressed("move_left"))

    def test_pressed_returns_false_for_inactive_action(self) -> None:
        keys = _KeyStateFake({pygame.K_LEFT})
        adapter = PygameActionInput(keys)

        self.assertFalse(adapter.pressed("move_right"))

    def test_pressed_with_multiple_key_alternatives(self) -> None:
        keys = _KeyStateFake({pygame.K_a})
        adapter = PygameActionInput(keys)

        self.assertTrue(adapter.pressed("move_left"))

    def test_pressed_with_right_alternative_key(self) -> None:
        keys = _KeyStateFake({pygame.K_d})
        adapter = PygameActionInput(keys)

        self.assertTrue(adapter.pressed("move_right"))

    def test_default_keymap_contains_all_actions(self) -> None:
        expected_actions = {
            "move_left",
            "move_right",
            "shoot",
            "restart",
            "toggle_music",
            "quit",
            "start_game",
        }
        self.assertEqual(set(DEFAULT_ACTION_KEYMAP.keys()), expected_actions)

    def test_custom_keymap_overrides_default(self) -> None:
        custom_map = {"move_left": (pygame.K_j,)}
        keys = _KeyStateFake({pygame.K_j})
        adapter = PygameActionInput(keys, keymap=custom_map)

        self.assertTrue(adapter.pressed("move_left"))

    def test_pressed_handles_unknown_action(self) -> None:
        keys = _KeyStateFake({pygame.K_SPACE})
        adapter = PygameActionInput(keys)

        self.assertFalse(adapter.pressed("nonexistent_action"))


if __name__ == "__main__":
    unittest.main()
