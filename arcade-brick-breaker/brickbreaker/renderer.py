from __future__ import annotations

import pygame

from . import config
from .state import GameState


class GameRenderer:
    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.font = pygame.font.SysFont("consolas", 30, bold=True)
        self.title_font = pygame.font.SysFont("consolas", 64, bold=True)
        self.body_font = pygame.font.SysFont("consolas", 28, bold=False)

    def draw(self, state: GameState) -> None:
        if state.menu_active:
            self._draw_start_menu()
            pygame.display.flip()
            return

        self.screen.fill(config.BACKGROUND_COLOR)

        pygame.draw.rect(self.screen, config.WALL_COLOR, (0, 0, config.SCREEN_WIDTH, 8))
        pygame.draw.rect(self.screen, config.WALL_COLOR, (0, 0, 8, config.SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, config.WALL_COLOR, (config.SCREEN_WIDTH - 8, 0, 8, config.SCREEN_HEIGHT))

        pygame.draw.rect(self.screen, config.PADDLE_COLOR, state.paddle.rect, border_radius=8)
        pygame.draw.ellipse(self.screen, config.BALL_COLOR, state.ball.rect)

        for brick in state.bricks:
            if brick.alive:
                pygame.draw.rect(self.screen, brick.color, brick.rect, border_radius=4)

        self._draw_hud(state)

        if state.game_over:
            self._draw_message("Game Over - SPACE to restart, ESC for menu")
        elif state.level_cleared:
            self._draw_message("Level Clear - SPACE for next level")
        elif state.paused:
            pause_overlay = pygame.Surface((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.SRCALPHA)
            pause_overlay.fill((*config.PAUSE_OVERLAY_COLOR, 180))
            self.screen.blit(pause_overlay, (0, 0))
            self._draw_message("Paused - ESC to resume")
        elif not state.started:
            self._draw_message("Press SPACE to launch")

        pygame.display.flip()

    def _draw_hud(self, state: GameState) -> None:
        score_text = self.font.render(f"Score: {state.score}", True, config.TEXT_COLOR)
        high_score_text = self.font.render(f"High Score: {state.high_score}", True, config.ACCENT_COLOR)
        lives_text = self.font.render(f"Lives: {state.lives}", True, config.TEXT_COLOR)
        level_text = self.font.render(f"Level: {state.level}", True, config.TEXT_COLOR)
        sfx_text = self.font.render(f"SFX: {'ON' if state.sfx_enabled else 'OFF'}", True, config.TEXT_COLOR)

        self.screen.blit(score_text, (18, 14))
        self.screen.blit(high_score_text, (18, 48))
        self.screen.blit(level_text, (config.SCREEN_WIDTH // 2 - (level_text.get_width() // 2), 14))
        self.screen.blit(lives_text, (config.SCREEN_WIDTH - lives_text.get_width() - 18, 14))
        self.screen.blit(sfx_text, (config.SCREEN_WIDTH - sfx_text.get_width() - 18, 48))

    def _draw_message(self, message: str) -> None:
        text = self.font.render(message, True, config.TEXT_COLOR)
        shadow = self.font.render(message, True, (0, 0, 0))
        x = (config.SCREEN_WIDTH - text.get_width()) // 2
        y = config.SCREEN_HEIGHT // 2
        self.screen.blit(shadow, (x + 2, y + 2))
        self.screen.blit(text, (x, y))

    def _draw_start_menu(self) -> None:
        self.screen.fill(config.MENU_OVERLAY_COLOR)

        title = self.title_font.render("BRICK BREAKER", True, config.ACCENT_COLOR)
        subtitle = self.body_font.render("Arcade Mode", True, config.TEXT_COLOR)
        tip_1 = self.body_font.render("Move: Left/Right or A/D", True, config.TEXT_COLOR)
        tip_2 = self.body_font.render("SPACE: Start / Launch", True, config.TEXT_COLOR)
        tip_3 = self.body_font.render("ESC: Pause / Resume", True, config.TEXT_COLOR)
        tip_4 = self.body_font.render("M: Toggle sound effects", True, config.TEXT_COLOR)

        title_x = (config.SCREEN_WIDTH - title.get_width()) // 2
        self.screen.blit(title, (title_x, 180))
        self.screen.blit(subtitle, ((config.SCREEN_WIDTH - subtitle.get_width()) // 2, 250))
        self.screen.blit(tip_1, ((config.SCREEN_WIDTH - tip_1.get_width()) // 2, 330))
        self.screen.blit(tip_2, ((config.SCREEN_WIDTH - tip_2.get_width()) // 2, 370))
        self.screen.blit(tip_3, ((config.SCREEN_WIDTH - tip_3.get_width()) // 2, 410))
        self.screen.blit(tip_4, ((config.SCREEN_WIDTH - tip_4.get_width()) // 2, 450))
