from __future__ import annotations

import json
import random

import pygame

from . import config
from .models import Ball, Brick, Paddle
from .state import GameState


def load_high_score() -> int:
    if not config.HIGH_SCORE_FILE.exists():
        return 0

    try:
        payload = json.loads(config.HIGH_SCORE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return 0

    return max(0, int(payload.get("high_score", 0)))


def save_high_score(value: int) -> None:
    try:
        config.HIGH_SCORE_FILE.write_text(
            json.dumps({"high_score": max(0, int(value))}, indent=2),
            encoding="utf-8",
        )
    except OSError:
        # High score save failures should never crash gameplay.
        return


def _brick_color_for_row(row: int) -> tuple[int, int, int]:
    if row < len(config.BRICK_COLORS):
        return config.BRICK_COLORS[row]
    return config.BRICK_COLORS[-1]


def create_bricks(level: int) -> list[Brick]:
    bricks: list[Brick] = []
    rows = min(config.BRICK_ROWS + (level - 1), config.BRICK_ROWS + 4)
    total_gap = (config.BRICK_COLUMNS - 1) * config.BRICK_GAP
    usable_width = config.SCREEN_WIDTH - (2 * config.BRICK_SIDE_PADDING) - total_gap
    brick_width = usable_width // config.BRICK_COLUMNS
    block_height = rows * config.BRICK_HEIGHT + (rows - 1) * config.BRICK_GAP
    paddle_y = config.SCREEN_HEIGHT - 70
    max_top_offset = paddle_y - config.BRICK_MIN_PADDLE_GAP - block_height
    top_offset = min(config.BRICK_TOP_OFFSET, max_top_offset)

    for row in range(rows):
        for col in range(config.BRICK_COLUMNS):
            x = config.BRICK_SIDE_PADDING + col * (brick_width + config.BRICK_GAP)
            y = top_offset + row * (config.BRICK_HEIGHT + config.BRICK_GAP)
            rect = pygame.Rect(x, y, brick_width, config.BRICK_HEIGHT)
            bricks.append(Brick(rect=rect, color=_brick_color_for_row(row)))

    return bricks


def create_initial_state() -> GameState:
    paddle_rect = pygame.Rect(
        (config.SCREEN_WIDTH - config.PADDLE_WIDTH) // 2,
        config.SCREEN_HEIGHT - 70,
        config.PADDLE_WIDTH,
        config.PADDLE_HEIGHT,
    )
    paddle = Paddle(rect=paddle_rect, speed=config.PADDLE_SPEED)

    ball_rect = pygame.Rect(0, 0, config.BALL_SIZE, config.BALL_SIZE)
    ball_rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
    ball = Ball(
        rect=ball_rect,
        velocity=pygame.Vector2(config.BALL_START_SPEED_X, config.BALL_START_SPEED_Y),
    )

    return GameState(
        paddle=paddle,
        ball=ball,
        bricks=create_bricks(level=1),
        score=0,
        high_score=load_high_score(),
        lives=config.START_LIVES,
        level=1,
        started=False,
        menu_active=True,
        paused=False,
        sfx_enabled=True,
        game_over=False,
        level_cleared=False,
    )


def _apply_level_difficulty(state: GameState) -> None:
    shrunk_width = max(
        config.PADDLE_MIN_WIDTH,
        config.PADDLE_WIDTH - ((state.level - 1) * config.PADDLE_SHRINK_PER_LEVEL),
    )
    state.paddle.rect.width = shrunk_width
    if state.paddle.rect.right > config.SCREEN_WIDTH:
        state.paddle.rect.right = config.SCREEN_WIDTH


def reset_ball_and_paddle(state: GameState) -> None:
    state.paddle.rect.centerx = config.SCREEN_WIDTH // 2
    state.paddle.rect.y = config.SCREEN_HEIGHT - 70

    state.ball.rect.center = (config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2)
    base_x = config.BALL_START_SPEED_X + ((state.level - 1) * config.BALL_LEVEL_SPEED_STEP)
    base_y = abs(config.BALL_START_SPEED_Y) + ((state.level - 1) * config.BALL_LEVEL_SPEED_STEP)
    start_x = random.choice([-1, 1]) * min(base_x, config.MAX_BALL_SPEED)
    start_y = -min(base_y, config.MAX_BALL_SPEED)
    state.ball.velocity = pygame.Vector2(start_x, start_y)
    state.started = False


def restart_game(state: GameState) -> None:
    state.score = 0
    state.level = 1
    state.lives = config.START_LIVES
    state.menu_active = False
    state.paused = False
    state.game_over = False
    state.level_cleared = False
    state.bricks = create_bricks(level=state.level)
    _apply_level_difficulty(state)
    reset_ball_and_paddle(state)


def start_next_level(state: GameState) -> None:
    state.level = min(state.level + 1, config.MAX_LEVEL)
    state.level_cleared = False
    state.game_over = False
    state.menu_active = False
    state.paused = False
    state.bricks = create_bricks(level=state.level)
    _apply_level_difficulty(state)
    reset_ball_and_paddle(state)
    state.started = True
