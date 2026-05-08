import random

from .config import (
    ALIEN_COLS,
    ALIEN_DESCEND,
    ALIEN_ROWS,
    ALIEN_START_X,
    ALIEN_X_GAP,
    BASE_ALIEN_STEP_INTERVAL,
    BUNKER_BLOCK_SIZE,
    ENEMY_SHOT_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)
from .geometry import Rect
from .models import Alien, Bullet, Explosion, MysteryShip
from .ports import AudioPort
from .state import GameState


def alive_aliens(aliens: list[Alien]) -> list[Alien]:
    return [alien for alien in aliens if alien.alive]


def alien_bounds(aliens: list[Alien]) -> tuple[float, float] | None:
    alive = alive_aliens(aliens)
    if not alive:
        return None
    left = min(alien.x for alien in alive)
    right = max(alien.x + alien.w for alien in alive)
    return left, right


def spawn_mystery_ship(state: GameState, sound: AudioPort) -> None:
    if state.mystery_ship is not None:
        return

    if random.random() < 0.5:
        state.mystery_ship = MysteryShip(-60, 46, 54, 22, 120)
    else:
        state.mystery_ship = MysteryShip(SCREEN_WIDTH + 10, 46, 54, 22, -120)

    sound.play("ufo")


def step_aliens(state: GameState, dt: float, sound: AudioPort) -> None:
    alive = alive_aliens(state.aliens)
    if not alive:
        return

    progress = len(alive) / (ALIEN_ROWS * ALIEN_COLS)
    interval = max(0.08, BASE_ALIEN_STEP_INTERVAL * progress * (0.96 ** (state.wave - 1)))

    state.alien_step_timer += dt
    if state.alien_step_timer < interval:
        return

    state.alien_step_timer = 0.0
    bounds = alien_bounds(state.aliens)
    if bounds is None:
        return

    left, right = bounds
    step_x = 8 * state.alien_direction
    hit_wall = (right + step_x >= SCREEN_WIDTH - 24) or (left + step_x <= 24)

    if hit_wall:
        state.alien_direction *= -1
        for alien in alive:
            alien.y += ALIEN_DESCEND
    else:
        for alien in alive:
            alien.x += step_x

    sound.play_alien_step()


def try_enemy_fire(state: GameState, dt: float) -> None:
    alive = alive_aliens(state.aliens)
    if not alive:
        return

    state.enemy_fire_timer -= dt
    if state.enemy_fire_timer > 0:
        return

    state.enemy_fire_timer = random.uniform(0.32, 0.9)

    columns: dict[int, Alien] = {}
    for alien in alive:
        col = int((alien.x - ALIEN_START_X + ALIEN_X_GAP / 2) // ALIEN_X_GAP)
        if col not in columns or alien.y > columns[col].y:
            columns[col] = alien

    shooters = list(columns.values())
    if not shooters:
        return

    shooter = random.choice(shooters)
    state.bullets.append(Bullet(shooter.x + shooter.w / 2, shooter.y + shooter.h + 2, ENEMY_SHOT_SPEED, True))


def damage_bunker_at(state: GameState, x: float, y: float) -> bool:
    hit_index = None
    for index, block in enumerate(state.bunker_blocks):
        if block.collidepoint(x, y):
            hit_index = index
            break

    if hit_index is None:
        return False

    del state.bunker_blocks[hit_index]

    if random.random() < 0.55 and state.bunker_blocks:
        nearby = [
            i
            for i, block in enumerate(state.bunker_blocks)
            if abs(block.centerx - x) <= BUNKER_BLOCK_SIZE and abs(block.centery - y) <= BUNKER_BLOCK_SIZE
        ]
        if nearby:
            del state.bunker_blocks[random.choice(nearby)]

    return True


def handle_collisions(state: GameState, sound: AudioPort) -> None:
    kept_bullets: list[Bullet] = []

    for bullet in state.bullets:
        if not (0 <= bullet.y <= SCREEN_HEIGHT):
            continue

        if damage_bunker_at(state, bullet.x, bullet.y):
            continue

        if bullet.from_enemy:
            if state.player_invuln <= 0 and state.player.collidepoint(bullet.x, bullet.y):
                state.lives -= 1
                state.player_invuln = 1.2
                state.explosions.append(Explosion(state.player.centerx, state.player.centery, 0.35, 0.35))
                sound.play("player_hit")
                if state.lives <= 0:
                    state.game_over = True
                continue
        else:
            hit_alien = False
            for alien in state.aliens:
                if alien.alive and Rect(alien.x, alien.y, alien.w, alien.h).collidepoint(bullet.x, bullet.y):
                    alien.alive = False
                    state.score += alien.points
                    state.explosions.append(Explosion(bullet.x, bullet.y, 0.22, 0.22))
                    sound.play("alien_hit")
                    hit_alien = True
                    break

            if hit_alien:
                continue

            if state.mystery_ship and state.mystery_ship.alive:
                ship_rect = Rect(
                    state.mystery_ship.x,
                    state.mystery_ship.y,
                    state.mystery_ship.w,
                    state.mystery_ship.h,
                )
                if ship_rect.collidepoint(bullet.x, bullet.y):
                    state.mystery_ship.alive = False
                    state.score += random.choice([100, 150, 200, 300])
                    state.explosions.append(Explosion(bullet.x, bullet.y, 0.28, 0.28))
                    sound.play("alien_hit")
                    continue

        kept_bullets.append(bullet)

    state.bullets = kept_bullets


def check_lose_by_descent(state: GameState) -> None:
    if state.game_over:
        return

    for alien in alive_aliens(state.aliens):
        if alien.y + alien.h >= state.player.y:
            state.game_over = True
            return
