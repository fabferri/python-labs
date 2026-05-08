# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Input adapter mapping keys to semantic actions.

from __future__ import annotations

from typing import Mapping

import pygame

from .ports import ActionInput, KeyState


DEFAULT_ACTION_KEYMAP: dict[str, tuple[int, ...]] = {
    "move_left": (pygame.K_LEFT, pygame.K_a),
    "move_right": (pygame.K_RIGHT, pygame.K_d),
    "move_up": (pygame.K_UP, pygame.K_w),
    "move_down": (pygame.K_DOWN, pygame.K_s),
    "start_game": (pygame.K_RETURN, pygame.K_SPACE),
    "difficulty_next": (pygame.K_RIGHT, pygame.K_d),
    "difficulty_prev": (pygame.K_LEFT, pygame.K_a),
    "difficulty_easy": (pygame.K_1,),
    "difficulty_normal": (pygame.K_2,),
    "difficulty_hard": (pygame.K_3,),
    "next_theme": (pygame.K_t,),
    "restart": (pygame.K_r,),
    "toggle_audio": (pygame.K_m,),
    "toggle_audio_menu": (pygame.K_s,),
    "quit": (pygame.K_ESCAPE,),
}


class PygameActionInput(ActionInput):
    # Initialize object state and dependencies.
    def __init__(
        self,
        keys: KeyState,
        keymap: Mapping[str, tuple[int, ...]] | None = None,
    ) -> None:
        self._keys = keys
        self._keymap = dict(keymap or DEFAULT_ACTION_KEYMAP)

    # Return whether the given semantic action is currently pressed.
    def pressed(self, action: str) -> bool:
        return any(self._keys[key] for key in self._keymap.get(action, ()))

    @staticmethod
    # Resolve the semantic action for a pressed key.
    def action_for_key(
        key: int,
        keymap: Mapping[str, tuple[int, ...]] | None = None,
    ) -> str | None:
        for action, keys in (keymap or DEFAULT_ACTION_KEYMAP).items():
            if key in keys:
                return action
        return None


