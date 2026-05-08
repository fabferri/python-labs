# ============================================================
# Pacman Arcade - Python Script
# ============================================================
# Purpose: Menu, HUD, and overlay message UI helpers.

from __future__ import annotations

import pygame


# Draw HUD values such as score, lives, and level.
def draw_hud(
    screen: pygame.Surface,
    font: pygame.font.Font,
    score: int,
    high_score: int,
    lives: int,
    level: int,
    sound_enabled: bool,
    screen_width: int,
    y_offset: int,
) -> None:
    score_text = font.render(f"SCORE {score}", True, (255, 214, 10))
    high_text = font.render(f"BEST {high_score}", True, (170, 255, 120))
    lives_text = font.render(f"LIVES {lives}", True, (248, 98, 174))
    level_text = font.render(f"LEVEL {level}", True, (255, 166, 102))
    sound_text = font.render(f"SOUND {'ON' if sound_enabled else 'OFF'} (M)", True, (133, 230, 255))

    screen.blit(score_text, (12, y_offset))
    screen.blit(high_text, (12, y_offset + 24))
    screen.blit(lives_text, (screen_width // 2 - lives_text.get_width() // 2, y_offset))
    screen.blit(level_text, (screen_width // 2 - level_text.get_width() // 2, y_offset + 24))
    screen.blit(sound_text, (screen_width - sound_text.get_width() - 12, y_offset))


# Draw a centered overlay message.
def draw_message(screen: pygame.Surface, font: pygame.font.Font, text: str, width: int, height: int) -> None:
    msg = font.render(text, True, (255, 255, 255))
    bg = pygame.Surface((msg.get_width() + 20, msg.get_height() + 14), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 180))
    x = width // 2 - bg.get_width() // 2
    y = height // 2 - bg.get_height() // 2
    screen.blit(bg, (x, y))
    screen.blit(msg, (x + 10, y + 7))


# Draw the start menu screen and current selections.
def draw_start_menu(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    width: int,
    height: int,
    high_score: int,
    sound_enabled: bool,
    difficulty_name: str,
    theme_name: str,
) -> None:
    title = title_font.render("PACMAN ARCADE", True, (255, 228, 87))
    line_1 = body_font.render("Press ENTER to start", True, (255, 255, 255))
    line_2 = body_font.render("Move: Arrows or WASD", True, (180, 230, 255))
    line_3 = body_font.render("Difficulty: Left/Right or 1/2/3", True, (180, 230, 255))
    line_4 = body_font.render(f"Selected: {difficulty_name}", True, (255, 200, 130))
    line_5 = body_font.render(f"Theme: {theme_name} (T)", True, (145, 240, 255))
    line_6 = body_font.render("Toggle Sound: M or S", True, (180, 230, 255))
    line_7 = body_font.render(f"High Score: {high_score}", True, (170, 255, 120))
    line_8 = body_font.render(f"Sound: {'ON' if sound_enabled else 'OFF'}", True, (255, 170, 130))

    center_x = width // 2
    y = height // 2 - 165
    for surface in [title, line_1, line_2, line_3, line_4, line_5, line_6, line_7, line_8]:
        screen.blit(surface, (center_x - surface.get_width() // 2, y))
        y += 40

