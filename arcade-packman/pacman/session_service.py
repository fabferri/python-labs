# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Session lifecycle management for start/load/reset.

from __future__ import annotations

from .config import DIFFICULTIES, PELLET_TYPES
from .factories import build_ghosts, get_ghost_spawns, get_player_spawn, split_pellets
from .level import load_level
from .models import DifficultyConfig
from .state import GameState


class SessionService:
    # Return the selected difficulty configuration.
    def current_difficulty(self, state: GameState) -> DifficultyConfig:
        return DIFFICULTIES[state.selected_difficulty]

    # Return the active visual theme name.
    def current_theme_name(self, state: GameState, theme_names: list[str]) -> str:
        return theme_names[state.selected_theme % len(theme_names)]

    # Load the current level and rebuild its runtime entities.
    def load_current_level(self, state: GameState) -> None:
        state.level = load_level(state.level_index)
        state.player_spawn = get_player_spawn(state.level)
        seed = (state.level_index + 1) * 100 + state.selected_difficulty
        state.pellets = split_pellets(set(state.level.pellets), PELLET_TYPES, seed)
        state.ghosts = build_ghosts(state.level, state.level_index, self.current_difficulty(state))
        self.reset_positions(state)

    # Reset player and ghost positions to their spawn points.
    def reset_positions(self, state: GameState) -> None:
        state.player.spawn(state.player_spawn)
        for ghost, spawn in zip(state.ghosts, get_ghost_spawns(state.level)):
            ghost.spawn(spawn)

    # Reset campaign progress and start a fresh run.
    def start_new_game(self, state: GameState) -> None:
        state.score = 0
        state.lives = 3
        state.level_index = 0
        state.game_over = False
        state.campaign_win = False
        state.game_state = "playing"
        self.load_current_level(state)

