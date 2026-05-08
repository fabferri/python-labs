# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Service that applies player intent to state.

from __future__ import annotations

from typing import Mapping

from .state import GameState


class PlayerController:
    ACTION_TO_DIRECTION: Mapping[str, tuple[int, int]] = {
        "move_left": (-1, 0),
        "move_right": (1, 0),
        "move_up": (0, -1),
        "move_down": (0, 1),
    }

    # Apply a semantic action to player movement intent.
    def handle_action(self, state: GameState, action: str | None) -> None:
        if not action or state.game_state != "playing":
            return
        direction = self.ACTION_TO_DIRECTION.get(action)
        if direction:
            state.player.set_next_direction(*direction)

