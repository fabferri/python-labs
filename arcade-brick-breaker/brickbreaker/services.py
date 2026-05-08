from __future__ import annotations

from . import config
from .factories import restart_game, start_next_level
from .ports import ActionInput
from .state import GameState
from .systems import update_world


class PlayerController:
    def update(self, state: GameState, controls: ActionInput) -> None:
        if state.menu_active or state.paused:
            return

        move = 0
        if controls.pressed("move_left"):
            move -= 1
        if controls.pressed("move_right"):
            move += 1

        state.paddle.rect.x += move * state.paddle.speed
        state.paddle.rect.x = max(0, min(state.paddle.rect.x, config.SCREEN_WIDTH - state.paddle.rect.width))


class EventController:
    def handle_action(self, state: GameState, action: str | None) -> str | None:
        if not action:
            return None

        if action == "toggle_sfx":
            state.sfx_enabled = not state.sfx_enabled
            return "sfx-off" if not state.sfx_enabled else "sfx-on"

        if action == "pause_menu":
            if state.menu_active:
                return None
            if state.game_over or state.level_cleared:
                state.menu_active = True
                state.started = False
                state.paused = False
                return "menu"
            state.paused = not state.paused
            return "pause" if state.paused else "resume"

        if action in {"start_launch", "restart"}:
            if state.menu_active:
                restart_game(state)
                state.started = True
                return "start"
            if state.game_over:
                restart_game(state)
                state.started = True
                return "restart"
            if state.level_cleared:
                start_next_level(state)
                return "next-level"
            if not state.started:
                state.started = True
                return "launch"

        return None


class WorldUpdater:
    def update(self, state: GameState) -> str:
        return update_world(state)
