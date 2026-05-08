from __future__ import annotations

from . import config
from .factories import reset_ball_and_paddle, save_high_score
from .models import Ball
from .state import GameState


def _speed_up_ball(ball: Ball) -> None:
    speed_x = min(abs(ball.velocity.x) + 0.08, config.MAX_BALL_SPEED)
    speed_y = min(abs(ball.velocity.y) + 0.05, config.MAX_BALL_SPEED)
    ball.velocity.x = speed_x if ball.velocity.x >= 0 else -speed_x
    ball.velocity.y = speed_y if ball.velocity.y >= 0 else -speed_y


def update_world(state: GameState) -> str:
    if state.menu_active or state.paused:
        return "idle"
    if not state.started or state.game_over or state.level_cleared:
        return "idle"

    ball = state.ball
    paddle = state.paddle
    event_outcome = "none"

    ball.rect.x += int(ball.velocity.x)
    ball.rect.y += int(ball.velocity.y)

    if ball.rect.left <= 0:
        ball.rect.left = 0
        ball.velocity.x *= -1
    elif ball.rect.right >= config.SCREEN_WIDTH:
        ball.rect.right = config.SCREEN_WIDTH
        ball.velocity.x *= -1

    if ball.rect.top <= 0:
        ball.rect.top = 0
        ball.velocity.y *= -1

    if ball.rect.colliderect(paddle.rect) and ball.velocity.y > 0:
        impact_pos = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
        ball.velocity.x = impact_pos * config.MAX_BALL_SPEED
        ball.velocity.y *= -1
        ball.rect.bottom = paddle.rect.top
        event_outcome = "paddle"

    for brick in state.bricks:
        if not brick.alive:
            continue
        if not ball.rect.colliderect(brick.rect):
            continue

        brick.alive = False
        state.score += config.BRICK_POINTS.get(brick.color, 1)
        if state.score > state.high_score:
            state.high_score = state.score
            save_high_score(state.high_score)
        _speed_up_ball(ball)
        event_outcome = "brick"

        overlap_left = ball.rect.right - brick.rect.left
        overlap_right = brick.rect.right - ball.rect.left
        overlap_top = ball.rect.bottom - brick.rect.top
        overlap_bottom = brick.rect.bottom - ball.rect.top

        min_overlap_x = min(overlap_left, overlap_right)
        min_overlap_y = min(overlap_top, overlap_bottom)

        if min_overlap_x < min_overlap_y:
            ball.velocity.x *= -1
        else:
            ball.velocity.y *= -1
        break

    if ball.rect.top > config.SCREEN_HEIGHT:
        state.lives -= 1
        if state.lives <= 0:
            state.game_over = True
            state.started = False
            event_outcome = "game-over"
        else:
            reset_ball_and_paddle(state)
            event_outcome = "life-lost"

    if all(not brick.alive for brick in state.bricks):
        state.level_cleared = True
        state.started = False
        event_outcome = "level-cleared"

    return event_outcome
