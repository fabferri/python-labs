# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Frame renderer and HUD/menu drawing orchestration.

from __future__ import annotations

from collections.abc import Mapping

import pygame

from .config import CFG
from .models import PelletType
from .sprites import SpriteBank, draw_ghost, draw_pacman, draw_pellet
from .state import GameState
from .ui import draw_hud, draw_message, draw_start_menu


class GameRenderer:
    # Initialize object state and dependencies.
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.hud_height = CFG.tile_size * 2
        self.game_area_height = CFG.screen_height - self.hud_height
        self.hud_font = pygame.font.SysFont("consolas", 24, bold=True)
        self.menu_font = pygame.font.SysFont("consolas", 28, bold=True)
        self.msg_font = pygame.font.SysFont("consolas", 34, bold=True)

    # Draw.
    def draw(
        self,
        state: GameState,
        sprites: SpriteBank,
        sound_enabled: bool,
        difficulty_name: str,
        theme_name: str,
        pellet_types: Mapping[str, PelletType],
    ) -> None:
        self.screen.fill((6, 8, 18))

        if state.game_state == "menu":
            draw_start_menu(
                screen=self.screen,
                title_font=self.msg_font,
                body_font=self.menu_font,
                width=CFG.screen_width,
                height=self.game_area_height,
                high_score=state.high_score,
                sound_enabled=sound_enabled,
                difficulty_name=difficulty_name,
                theme_name=theme_name,
            )
        else:
            self._draw_world(state, sprites, pellet_types)
            draw_hud(
                screen=self.screen,
                font=self.hud_font,
                score=state.score,
                high_score=state.high_score,
                lives=state.lives,
                level=state.level_index + 1,
                sound_enabled=sound_enabled,
                screen_width=CFG.screen_width,
                y_offset=CFG.screen_height - self.hud_height + 4,
            )

            if state.game_state == "campaign_win":
                draw_message(
                    self.screen,
                    self.msg_font,
                    "ALL LEVELS CLEAR! PRESS R",
                    CFG.screen_width,
                    self.game_area_height,
                )
            elif state.game_state == "game_over":
                draw_message(
                    self.screen,
                    self.msg_font,
                    "GAME OVER! PRESS R",
                    CFG.screen_width,
                    self.game_area_height,
                )

        pygame.display.flip()

    # Helper: Draw World.
    def _draw_world(
        self,
        state: GameState,
        sprites: SpriteBank,
        pellet_types: Mapping[str, PelletType],
    ) -> None:
        for x, y in state.level.walls:
            wall_rect = pygame.Rect(
                x * CFG.tile_size,
                y * CFG.tile_size,
                CFG.tile_size,
                CFG.tile_size,
            )
            pygame.draw.rect(self.screen, (26, 66, 154), wall_rect, border_radius=5)
            pygame.draw.rect(self.screen, (72, 154, 255), wall_rect, 1, border_radius=5)

        for pellet_type in pellet_types:
            for x, y in state.pellets[pellet_type]:
                pellet_pos = (
                    int((x + 0.5) * CFG.tile_size),
                    int((y + 0.5) * CFG.tile_size),
                )
                variant_mod = 2 if pellet_type in ("rare", "treasure", "super") else 3
                variant = (x * 31 + y * 17 + state.level_index * 13 + len(pellet_type)) % variant_mod
                draw_pellet(
                    self.screen,
                    sprites,
                    pellet_pos,
                    state.elapsed_time,
                    kind=pellet_type,
                    theme_index=state.selected_theme,
                    variant_index=variant,
                )

        draw_pacman(
            screen=self.screen,
            bank=sprites,
            center=(int(state.player.position.x), int(state.player.position.y)),
            direction=state.player_facing,
            time_s=state.elapsed_time,
            style_index=state.selected_theme,
        )

        for ghost in state.ghosts:
            draw_ghost(
                screen=self.screen,
                bank=sprites,
                center=(int(ghost.position.x), int(ghost.position.y)),
                ghost_sprite_index=ghost.sprite_index,
                time_s=state.elapsed_time,
                theme_index=state.selected_theme,
            )


