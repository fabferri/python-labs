import random
from typing import Callable

from .config import PLAYER_SHOT_SPEED, PLAYER_SPEED, SCREEN_WIDTH
from .models import Bullet
from .ports import ActionInput, AudioPort
from .state import GameState
from .systems import (
    alive_aliens,
    check_lose_by_descent,
    handle_collisions,
    spawn_mystery_ship,
    step_aliens,
    try_enemy_fire,
)


class PlayerController:
    def update(self, state: GameState, dt: float, controls: ActionInput, sound: AudioPort) -> None:
        move = 0
        if controls.pressed("move_left"):
            move -= 1
        if controls.pressed("move_right"):
            move += 1

        state.player.x += int(move * PLAYER_SPEED * dt)
        state.player.x = max(20, min(SCREEN_WIDTH - state.player.width - 20, state.player.x))

        state.player_cooldown = max(0.0, state.player_cooldown - dt)
        state.player_invuln = max(0.0, state.player_invuln - dt)

        if controls.pressed("shoot") and state.player_cooldown <= 0:
            player_bullets = [bullet for bullet in state.bullets if not bullet.from_enemy]
            if len(player_bullets) < 2:
                state.bullets.append(Bullet(state.player.centerx, state.player.y - 4, PLAYER_SHOT_SPEED, False))
                state.player_cooldown = 0.22
                sound.play("shoot")


class WorldUpdater:
    def update(self, state: GameState, dt: float, sound: AudioPort) -> None:
        for bullet in state.bullets:
            bullet.y += bullet.dy * dt

        step_aliens(state, dt, sound)
        try_enemy_fire(state, dt)

        state.mystery_spawn_timer -= dt
        if state.mystery_spawn_timer <= 0:
            spawn_mystery_ship(state, sound)
            state.mystery_spawn_timer = random.uniform(10.0, 18.0)

        if state.mystery_ship:
            state.mystery_ship.x += state.mystery_ship.dx * dt
            if (
                state.mystery_ship.x < -80
                or state.mystery_ship.x > SCREEN_WIDTH + 80
                or not state.mystery_ship.alive
            ):
                state.mystery_ship = None

        for explosion in state.explosions:
            explosion.ttl -= dt
        state.explosions = [explosion for explosion in state.explosions if explosion.ttl > 0]

        handle_collisions(state, sound)
        check_lose_by_descent(state)


class WaveManager:
    def update(self, state: GameState, dt: float, on_next_wave: Callable[[], None]) -> None:
        if not alive_aliens(state.aliens) and not state.game_over:
            state.victory_flash += dt
            if state.victory_flash > 0.7:
                state.victory_flash = 0.0
                on_next_wave()
