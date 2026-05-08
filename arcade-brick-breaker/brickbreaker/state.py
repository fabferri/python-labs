from __future__ import annotations

from dataclasses import dataclass

from .models import Ball, Brick, Paddle


@dataclass
class GameState:
    paddle: Paddle
    ball: Ball
    bricks: list[Brick]
    score: int
    high_score: int
    lives: int
    level: int
    started: bool
    menu_active: bool
    paused: bool
    sfx_enabled: bool
    game_over: bool
    level_cleared: bool
