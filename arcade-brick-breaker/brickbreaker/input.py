from __future__ import annotations

from typing import Mapping

import pygame

from .ports import ActionInput, KeyState


DEFAULT_ACTION_KEYMAP: dict[str, tuple[int, ...]] = {
    "move_left": (pygame.K_LEFT, pygame.K_a),
    "move_right": (pygame.K_RIGHT, pygame.K_d),
    "start_launch": (pygame.K_SPACE,),
    "restart": (pygame.K_r,),
    "pause_menu": (pygame.K_ESCAPE,),
    "toggle_sfx": (pygame.K_m,),
}


class PygameActionInput(ActionInput):
    def __init__(
        self,
        keys: KeyState,
        keymap: Mapping[str, tuple[int, ...]] | None = None,
    ) -> None:
        self._keys = keys
        self._keymap = dict(keymap or DEFAULT_ACTION_KEYMAP)

    def pressed(self, action: str) -> bool:
        return any(self._keys[key] for key in self._keymap.get(action, ()))

    @staticmethod
    def action_for_key(
        key: int,
        keymap: Mapping[str, tuple[int, ...]] | None = None,
    ) -> str | None:
        for action, keys in (keymap or DEFAULT_ACTION_KEYMAP).items():
            if key in keys:
                return action
        return None
