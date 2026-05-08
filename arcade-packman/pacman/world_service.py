# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: World-step orchestration and event emission service.

from __future__ import annotations

from typing import Mapping

from .config import PELLET_TYPES
from .events import WorldEvents
from .models import PelletType
from .state import GameState, resolve_level_completion
from .systems import all_pellets_cleared, advance_actors, consume_pellet_at_player, has_player_ghost_collision


class WorldUpdater:
    # Update.
    def update(
        self,
        state: GameState,
        pellet_types: Mapping[str, PelletType] = PELLET_TYPES,
    ) -> WorldEvents:
        events = WorldEvents()
        if state.game_state != "playing":
            return events

        advance_actors(state)

        pellet_eaten, pellet_sound = consume_pellet_at_player(state, pellet_types)
        if pellet_eaten:
            if state.score > state.high_score:
                state.high_score = state.score
                events.high_score_changed = True
            if pellet_sound:
                events.sounds.append(pellet_sound)

        if pellet_eaten and all_pellets_cleared(state):
            events.sounds.append("win")
            state.level_index, state.game_state, state.campaign_win = resolve_level_completion(
                state.level_index,
                state.level_count,
            )
            if state.game_state == "playing":
                events.request_load_current_level = True

        if has_player_ghost_collision(state):
            state.lives -= 1
            events.sounds.append("death")
            events.request_reset_positions = True
            if state.lives <= 0:
                state.game_over = True
                if state.score > state.high_score:
                    state.high_score = state.score
                    events.high_score_changed = True
                state.game_state = "game_over"

        return events

