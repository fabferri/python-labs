import unittest

import pygame

from brickbreaker.input import PygameActionInput


class FakeKeys:
    def __init__(self, pressed: set[int]) -> None:
        self._pressed = pressed

    def __getitem__(self, key: int) -> bool:
        return key in self._pressed


class InputTests(unittest.TestCase):
    def test_pressed_reports_true_for_mapped_action(self) -> None:
        keys = FakeKeys({pygame.K_LEFT})
        controls = PygameActionInput(keys)

        self.assertTrue(controls.pressed("move_left"))
        self.assertFalse(controls.pressed("move_right"))

    def test_action_for_key_maps_space_to_start_launch(self) -> None:
        self.assertEqual("start_launch", PygameActionInput.action_for_key(pygame.K_SPACE))

    def test_pressed_returns_false_for_unknown_action(self) -> None:
        keys = FakeKeys({pygame.K_LEFT, pygame.K_SPACE})
        controls = PygameActionInput(keys)

        self.assertFalse(controls.pressed("unknown_action"))

    def test_action_for_key_returns_none_for_unmapped_key(self) -> None:
        self.assertIsNone(PygameActionInput.action_for_key(pygame.K_F1))

    def test_action_for_key_supports_custom_keymap(self) -> None:
        custom_keymap = {"fire": (pygame.K_RETURN,)}
        self.assertEqual("fire", PygameActionInput.action_for_key(pygame.K_RETURN, custom_keymap))


if __name__ == "__main__":
    unittest.main()
